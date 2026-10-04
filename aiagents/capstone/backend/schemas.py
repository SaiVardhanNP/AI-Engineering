from typing import Literal

from pydantic import BaseModel, Field


class TicketRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=1, max_length=2000)
    # continue an existing conversation. Leave out to start a new one.
    conversation_id: str | None = Field(default=None, max_length=64)


# What a customer is allowed to see. Findings, evidence and reasons stay on the team side.
class TicketResponse(BaseModel):
    ticket_id: str | None
    conversation_id: str | None
    status: Literal["reply", "escalated"]
    reply: str
    # a person will follow up on this ticket even though the assistant answered it
    needs_human: bool = False
    categories: list[str]
    timings: dict[str, float]


# ---- team side ----


class TicketSummary(BaseModel):
    id: str
    customer_id: str
    customer_name: str
    message: str
    status: Literal["replied", "escalated"]
    review: Literal["none", "open", "resolved"]
    categories: list[str]
    escalation_reason: str | None
    created_at: str
    conversation_id: str | None = None
    message_count: int = 1


class ConversationTurn(BaseModel):
    ticket_id: str
    message: str
    reply: str | None
    status: Literal["replied", "escalated"]
    review: Literal["none", "open", "resolved"]
    human_reply: str | None
    created_at: str


class Conversation(BaseModel):
    conversation_id: str
    turns: list[ConversationTurn]


class Claim(BaseModel):
    statement: str
    supporting_quote: str | None


class TicketDetail(TicketSummary):
    reply: str | None
    draft: str | None
    findings: str | None
    attempts: list[dict]
    claims: list[Claim]
    timings: dict[str, float]
    human_reply: str | None
    resolved_at: str | None


class ResolveRequest(BaseModel):
    human_reply: str = Field(min_length=1, max_length=2000)
