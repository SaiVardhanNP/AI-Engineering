import time

from crewai import Crew, Process

from agents import build_agents
from crew_tools import build_tools
from dependencies import get_data_service, get_knowledge_service
from services.conversation_context import customer_words, frame_ticket
from services.handoff import check_handoff, handoff_reason
from services.reply_verifier import clean_clarify_reply, find_completed_action_claims, verify_claims
from tasks import (
    DOMAINS,
    build_investigation_tasks,
    evaluator_task,
    responder_task,
    revise_task,
    router_task,
)

MAX_RETRIES = 2


def _run_single(agent, task, verbose):
    return Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=verbose,
    ).kickoff()


def judge(evaluation, draft, findings, handoff=None):
    """Combine the LLM's view with the code checks. Returns (passed, feedback, problems).

    `handoff` is the reason a person must see this ticket, or None. What the reply
    says about a person has to match it."""
    problems = verify_claims(evaluation.claims, findings)
    problems += find_completed_action_claims(draft)
    problems += check_handoff(draft, handoff)

    passed = evaluation.relevant and evaluation.complete and not problems

    feedback_parts = []
    if not evaluation.relevant or not evaluation.complete:
        feedback_parts.append(evaluation.feedback)
    if problems:
        bullets = "\n- ".join(problems)
        feedback_parts.append(
            f"Fix these problems with the draft:\n- {bullets}"
        )

    return passed, "\n".join(part for part in feedback_parts if part), problems


def run_ticket(ticket, customer_id, verbose=False, activity=None, history=None):
    """Handle one customer message. `history` is the recent turns of the same
    conversation (oldest first), so a follow-up is understood in context."""
    framed = frame_ticket(ticket, history)
    customer_said = customer_words(ticket, history)

    tools = build_tools(customer_id, get_data_service(), get_knowledge_service())
    agents = build_agents(tools)

    def say(event_type, **data):
        if activity:
            activity.emit(event_type, **data)

    if activity:
        activity.watch(agents)

    timings = {}
    started = time.time()

    def lap(label):
        nonlocal started
        now = time.time()
        timings[label] = round(now - started, 1)
        started = now

    # 1. classify
    say("stage", stage="classifying", label="Reading your message")
    classification = _run_single(
        agents["router"], router_task(agents["router"], framed), verbose
    ).pydantic
    lap("classify")

    # only real specialist domains count. "clarify" and "other" are not domains.
    domains = [c for c in classification.categories if c in DOMAINS]
    say(
        "stage",
        stage="classified",
        label="Understood: "
        + (
            ", ".join(domains)
            if domains
            else "needs a person"
            if "other" in classification.categories
            else "a quick question"
        ),
        categories=classification.categories,
    )

    # a greeting, thanks, or a message too vague to act on gets an immediate
    # reply asking for details. No specialists run and no human is involved.
    if not domains and "other" not in classification.categories:
        return {
            "status": "reply",
            "reply": clean_clarify_reply(classification.reply, customer_said),
            "classification": classification.model_dump(),
            "findings": None,
            "attempts": [],
            "timings": timings,
        }

    if not domains:
        return {
            "status": "escalate",
            "reason": "ticket does not fit any support domain",
            "classification": classification.model_dump(),
            "timings": timings,
        }

    # Does a person have to see this? Decided from facts before anything is written,
    # so the reply can be honest about it: the router's "wants an action" flag, and
    # a direct database check for a duplicate charge that has not been refunded.
    duplicates = {}
    if "billing" in domains:
        duplicates = get_data_service().get_payment_details(customer_id).get("invoices_charged_more_than_once", {})
    handoff = handoff_reason(classification.wants_action, duplicates)

    # 2. investigate (independent domains in parallel) and draft the reply
    investigation = build_investigation_tasks(agents, framed, domains)
    first_draft = responder_task(agents["responder"], framed, list(investigation.values()), handoff=handoff)

    say("stage", stage="investigating", label="Investigating", domains=list(investigation))

    draft = Crew(
        agents=[agents[name] for name in investigation] + [agents["responder"]],
        tasks=[*investigation.values(), first_draft],
        process=Process.sequential,
        verbose=verbose,
    ).kickoff().raw
    lap("investigate_and_draft")

    findings = "\n\n".join(
        f"## {name.upper()} FINDINGS\n{task.output.raw}"
        for name, task in investigation.items()
    )

    # 3. evaluate, and revise up to MAX_RETRIES times
    attempts = []

    for attempt in range(MAX_RETRIES + 1):
        say("stage", stage="checking", label="Checking the reply against what we found", attempt=attempt + 1)
        evaluation = _run_single(
            agents["evaluator"],
            evaluator_task(agents["evaluator"], framed, findings, draft),
            verbose,
        ).pydantic
        lap(f"evaluate_{attempt + 1}")

        passed, feedback, problems = judge(evaluation, draft, findings, handoff)

        attempts.append(
            {
                "draft": draft,
                "relevant": evaluation.relevant,
                "complete": evaluation.complete,
                "problems": problems,
                "claims": [claim.model_dump() for claim in evaluation.claims],
                "passed": passed,
            }
        )

        if passed:
            return {
                "status": "reply",
                "reply": draft,
                "needs_human": handoff,
                "classification": classification.model_dump(),
                "findings": findings,
                "attempts": attempts,
                "timings": timings,
            }

        if attempt == MAX_RETRIES:
            break

        say(
            "stage",
            stage="revising",
            label=f"Fixing {len(problems) or 1} issue(s) found in the draft",
            attempt=attempt + 1,
        )
        draft = _run_single(
            agents["responder"],
            revise_task(agents["responder"], framed, findings, draft, feedback, handoff=handoff),
            verbose,
        ).raw
        lap(f"revise_{attempt + 1}")

    # 4. still failing after the retry limit: hand over to a human
    return {
        "status": "escalate",
        "reason": "reply failed evaluation after the retry limit",
        "last_draft": draft,
        "classification": classification.model_dump(),
        "findings": findings,
        "attempts": attempts,
        "timings": timings,
    }
