import json
import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from activity import ActivityStream
from config import settings
from database import ensure_tables
from dependencies import (
    get_conversation_store,
    get_data_service,
    get_knowledge_service,
    get_ticket_store,
)
from schemas import (
    Conversation,
    ResolveRequest,
    TicketDetail,
    TicketRequest,
    TicketResponse,
    TicketSummary,
)
from services.conversation_store import ConversationNotFound
from support_pipeline import run_ticket

logger = logging.getLogger("supportdesk")

ESCALATION_MESSAGE = (
    "Thanks for your patience. I've passed your ticket to a member of our "
    "support team, who will follow up with you."
)
UNAVAILABLE_MESSAGE = "The support assistant is unavailable right now"


@asynccontextmanager
async def lifespan(app):
    ensure_tables()
    # importing torch and loading the reranker takes a while, so do it once
    # at startup instead of during the first customer's request
    await run_in_threadpool(get_knowledge_service)
    yield


app = FastAPI(title="Support Desk API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _require_customer(customer_id):
    # The customer id comes from the request body only because this is a demo
    # with no login. In production it must come from the authenticated session.
    if "error" in get_data_service().get_account_status(customer_id):
        raise HTTPException(status_code=404, detail="Unknown customer")


def _prepare(request):
    """Check the customer, pick the conversation this message belongs to, and
    load its recent turns for the agents. Returns (conversation_id, history)."""
    _require_customer(request.customer_id)

    conversations = get_conversation_store()
    try:
        conversation_id = conversations.resolve(request.conversation_id, request.customer_id)
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail="Unknown conversation")

    return conversation_id, conversations.history(conversation_id)


def _finish(result, request, conversation_id):
    """Turn a pipeline result into the customer's response and store the ticket."""
    escalated = result["status"] != "reply"
    customer_reply = ESCALATION_MESSAGE if escalated else result["reply"]

    # a storage failure must never cost the customer their reply
    try:
        ticket_id = get_ticket_store().save(
            result, request.customer_id, request.message, customer_reply, conversation_id=conversation_id
        )
        get_conversation_store().touch(conversation_id)
    except Exception:
        logger.exception("could not store the ticket")
        ticket_id = None

    return TicketResponse(
        ticket_id=ticket_id,
        conversation_id=conversation_id,
        status="escalated" if escalated else "reply",
        reply=customer_reply,
        needs_human=bool(result.get("needs_human")) or escalated,
        categories=result.get("classification", {}).get("categories", []),
        timings=result.get("timings", {}),
    )


@app.get("/health")
def health():
    return {"status": "ok"}


# These are plain `def`, not `async def`, on purpose: the pipeline is blocking
# and CrewAI starts its own event loop internally. FastAPI runs plain `def`
# endpoints in a worker thread, where that is allowed.
@app.post("/tickets", response_model=TicketResponse)
def create_ticket(request: TicketRequest):
    conversation_id, history = _prepare(request)

    try:
        result = run_ticket(request.message, request.customer_id, history=history)
    except Exception:
        # keep model and tool details out of the response, but log them
        logger.exception("ticket pipeline failed")
        raise HTTPException(status_code=502, detail=UNAVAILABLE_MESSAGE)

    return _finish(result, request, conversation_id)


@app.post("/tickets/stream")
def stream_ticket(request: TicketRequest):
    """Same as POST /tickets, but streams what the assistant is doing as
    server-sent events, ending with a `done` event that carries the reply.

    Browsers' EventSource only supports GET, so the frontend reads this with
    fetch() and a streaming reader instead.
    """
    conversation_id, history = _prepare(request)

    activity = ActivityStream()
    activity.emit("stage", stage="started", label="Got your message")

    def work():
        try:
            result = run_ticket(request.message, request.customer_id, activity=activity, history=history)
            activity.emit("done", **_finish(result, request, conversation_id).model_dump())
        except Exception:
            logger.exception("ticket pipeline failed")
            activity.emit("error", message=UNAVAILABLE_MESSAGE)
        finally:
            activity.close()

    threading.Thread(target=work, daemon=True).start()

    def sse():
        for event in activity.events():
            if event is None:
                yield ": keepalive\n\n"  # a comment line, ignored by clients
            else:
                yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        sse(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---- team side ----
# These expose the AI's internal work (findings, evidence, drafts). The demo has
# no staff login, so they are open. Before real use they need authentication.


@app.get("/team/tickets", response_model=list[TicketSummary])
def list_tickets(
    status: str | None = Query(default=None, pattern="^(replied|escalated)$"),
    limit: int = Query(default=50, ge=1, le=200),
):
    return get_ticket_store().list(status=status, limit=limit)


@app.get("/team/tickets/{ticket_id}", response_model=TicketDetail)
def get_ticket(ticket_id: str):
    ticket = get_ticket_store().get(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Unknown ticket")
    return ticket


@app.post("/team/tickets/{ticket_id}/resolve", response_model=TicketDetail)
def resolve_ticket(ticket_id: str, request: ResolveRequest):
    store = get_ticket_store()

    if store.get(ticket_id) is None:
        raise HTTPException(status_code=404, detail="Unknown ticket")

    if not store.resolve(ticket_id, request.human_reply):
        raise HTTPException(status_code=409, detail="This ticket is not waiting for a human reply")

    return store.get(ticket_id)


# ---- conversations ----


@app.get("/conversations/{conversation_id}", response_model=Conversation)
def get_conversation(conversation_id: str, customer_id: str = Query(min_length=1, max_length=64)):
    """The customer's own view of a conversation. The chat uses it to come back
    after a page refresh and to pick up a reply from a human."""
    _require_customer(customer_id)

    try:
        turns = get_conversation_store().thread(conversation_id, customer_id=customer_id)
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail="Unknown conversation")

    return Conversation(conversation_id=conversation_id, turns=turns)


@app.get("/team/conversations/{conversation_id}", response_model=Conversation)
def get_team_conversation(conversation_id: str):
    try:
        turns = get_conversation_store().thread(conversation_id)
    except ConversationNotFound:
        raise HTTPException(status_code=404, detail="Unknown conversation")

    return Conversation(conversation_id=conversation_id, turns=turns)
