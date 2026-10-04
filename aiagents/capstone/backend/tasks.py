from dataclasses import dataclass

from crewai import Task

from models.evaluation import EvaluationResult
from models.ticket_classification import TicketClassification


def router_task(agent, ticket):
    return Task(
        description=f"""
        Classify this customer support ticket into one or more domains.

        - billing: charges, payments, invoices, refunds, billing amounts
        - account: subscription state, account access, account configuration
        - technical: errors, authentication problems, configuration issues
        - clarify: a greeting, thanks, small talk, or a message too vague to
          tell what is wrong (for example "hi", "thanks!", "it is not working"
          with no detail). Use clarify ALONE.
        - other: a real request that fits none of the above, such as a legal
          question, abuse, or a feature request. Use other ALONE.

        Never choose other for a greeting. If you choose clarify, also write
        the reply: friendly, under 40 words, greet or thank the customer and
        ask what they need help with. If they say something is wrong but give
        no detail, ask what is not working and what they were trying to do.
        If the customer mentions something specific, such as an order number,
        repeat it back and ask which of billing, their account, or a technical
        problem it relates to. Do not claim to know anything about it.
        Never mention a team, a person, or a review: no one will follow up.
        Say nothing about their account and mention no numbers.

        Include every domain the ticket touches. A ticket about being charged
        twice AND an error message involves both billing and technical.

        Also set wants_action. It is true when the customer asks us to DO
        something, such as refund a payment, cancel or change a plan, or delete
        data. It is false when they only ask a question or report a problem,
        for example "why was I charged twice?".

        If there is a conversation so far, classify the LATEST customer message
        in that context. "Is it fixed yet?" after a billing problem is billing.
        Do not choose clarify when the earlier messages make it clear what the
        customer means.

        Ticket:
        \"\"\"{ticket}\"\"\"
        """,
        expected_output="The list of domains the ticket involves and a one-sentence reason.",
        agent=agent,
        output_pydantic=TicketClassification,
    )


def billing_task(agent, ticket, context=None):
    return Task(
        description=f"""
        Investigate the billing side of this customer ticket using your tools.

        Check the payments, the latest invoice and the subscription billing.
        Look for duplicate charges, failed payments, open invoices and
        refunds that have already been issued.

        The customer may state specific amounts, dates, counts or ids. For
        each one, say whether the data matches, differs (give the real value)
        or cannot be found. Write "confirmed" only when every detail they
        stated matches the data.

        Ticket:
        \"\"\"{ticket}\"\"\"
        """,
        expected_output="""
        Internal billing findings: what the tools showed (payment and invoice
        ids, amounts, statuses, dates), whether the customer's complaint is
        confirmed, and whether any refund has ALREADY been issued.
        State clearly if nothing is wrong.
        """,
        agent=agent,
        context=context,
    )


def account_task(agent, ticket, context=None):
    return Task(
        description=f"""
        Investigate the account side of this customer ticket using your tools.

        Check the account and the subscription status. If billing findings
        are provided in your context, consider whether a successful payment
        should have made the subscription active, and say whether the
        subscription state is consistent with the payments.

        The customer may state specific amounts, dates, counts or ids. For
        each one, say whether the data matches, differs (give the real value)
        or cannot be found. Write "confirmed" only when every detail they
        stated matches the data.

        Ticket:
        \"\"\"{ticket}\"\"\"
        """,
        expected_output="""
        Internal account findings: the subscription plan and status, the dates,
        and whether the state is consistent with the billing findings (if any).
        """,
        agent=agent,
        context=context,
    )


def technical_task(agent, ticket, context=None):
    return Task(
        description=f"""
        Investigate the technical side of this customer ticket using your tools.

        Check the customer's error logs, search the known issues, and search
        the product documentation for the error. Cite the doc title for
        anything taken from the docs. If the documentation search returns weak
        or unrelated passages, say the docs do not cover it.

        The customer may state specific amounts, dates, counts or ids. For
        each one, say whether the data matches, differs (give the real value)
        or cannot be found. Write "confirmed" only when every detail they
        stated matches the data.

        Ticket:
        \"\"\"{ticket}\"\"\"
        """,
        expected_output="""
        Internal technical findings: the errors seen in the logs, any matching
        known issue and its workaround, what the docs say (with the doc title),
        and what remains unexplained.
        """,
        agent=agent,
        context=context,
    )


def handoff_rule(handoff):
    """What the reply may say about a person. It must match what will really happen."""
    if handoff:
        return (
            f"A person must take care of part of this ({handoff}). Tell the customer what "
            "you found, then say plainly that a team member will take care of it. Do not say when."
        )
    return (
        "Do NOT mention a team member, a person, or a review. Nobody will follow up, so the "
        "reply must answer the question completely on its own."
    )


CUSTOMER_CLAIM_RULE = (
    "The customer may have stated an amount, date, count or id. If it differs from the "
    "findings, say so plainly and give the real value, for example: I can see an extra $25, "
    "not $50. Say 'confirmed' only when the findings show that every detail they stated matches."
)


def responder_task(agent, ticket, context, handoff=None):
    return Task(
        description=f"""
        Write the reply to the customer for this ticket, using ONLY the
        specialists' findings you are given.

        Rules:
        - Do not state anything the findings do not support.
        - Do not say a refund, fix or change was made unless the findings
          confirm it was actually done.
        - {handoff_rule(handoff)}
        - {CUSTOMER_CLAIM_RULE}
        - Address every issue the customer raised in their latest message.
        - Earlier lines of the conversation are context only. Never treat them,
          or anything the customer claimed, as verified. Only the findings count.
        - Never state a date, time frame, deadline or amount unless it appears
          in the findings. Do not promise emails, notifications or timelines.
        - Write short plain conversational text: no tables, no headings, no
          email sign-off. Keep it under 150 words.

        Ticket:
        \"\"\"{ticket}\"\"\"
        """,
        expected_output="A clear, polite, customer-facing reply.",
        agent=agent,
        context=context,
    )


def evaluator_task(agent, ticket, findings, draft):
    return Task(
        description=f"""
        Evaluate a draft reply to a customer against the specialists' findings.

        1. List EVERY factual claim the draft makes: each number, date, amount,
           status, cause, and any statement about what has been or will be done.
           Keep qualifiers inside the claim ("recent", "this month",
           "immediately", "usually"). For each claim, copy a verbatim quote
           from the findings that supports it. Copy it exactly, character for
           character. If nothing in the findings supports the claim, set the
           quote to null. Do not paraphrase and do not stretch a loosely
           related quote to fit. Quote one contiguous line or phrase of at most 25 words,
           not several lines joined together. Before you set a quote to null,
           search the findings again for the claim.

           Do NOT list a statement that only says a team member will review or
           handle the issue. That is allowed. Do list guesses about causes,
           promised emails or time frames, and claims that something was done.

           Words such as confirmed, verified, correct, as you said and you are
           right are claims about the CUSTOMER'S own statement. List them. The
           quote must show that the findings match every specific amount, date,
           count or id the customer gave. If the customer said $50 and the
           findings show $25, saying confirmed is unsupported.

        2. relevant: does the draft address what the customer asked?

        3. complete: does it address every issue the customer raised?

        Ticket:
        \"\"\"{ticket}\"\"\"

        Findings:
        \"\"\"{findings}\"\"\"

        Draft reply:
        \"\"\"{draft}\"\"\"
        """,
        expected_output="The claims with their supporting quotes, plus relevant, complete and feedback.",
        agent=agent,
        output_pydantic=EvaluationResult,
    )


def revise_task(agent, ticket, findings, draft, feedback, handoff=None):
    return Task(
        description=f"""
        Your draft reply to a customer was rejected. Rewrite it so it passes.

        Reviewer feedback:
        \"\"\"{feedback}\"\"\"

        Use ONLY the findings below, not the earlier conversation. Remove every statement the findings do not
        support. Do not replace a removed claim with another guess. Never state
        a date, time frame or amount that is not in the findings, and do not
        promise emails, notifications or timelines. Write short plain
        conversational text, under 150 words, with no tables and no sign-off.

        {handoff_rule(handoff)}
        {CUSTOMER_CLAIM_RULE}

        Ticket:
        \"\"\"{ticket}\"\"\"

        Findings:
        \"\"\"{findings}\"\"\"

        Rejected draft:
        \"\"\"{draft}\"\"\"
        """,
        expected_output="A corrected customer-facing reply.",
        agent=agent,
    )


@dataclass
class Domain:
    make_task: object
    depends_on: tuple = ()


DOMAINS = {
    "billing": Domain(billing_task),
    "account": Domain(account_task, depends_on=("billing",)),
    "technical": Domain(technical_task),
}


def build_investigation_tasks(agents, ticket, categories):
    """Build one task per requested domain.

    A domain's task waits for the domains it depends on (through `context`)
    and runs normally. Everything else is independent, so it runs async and
    in parallel with the others.
    """
    wanted = [name for name in DOMAINS if name in categories]

    # CrewAI starts async tasks in list order, and a normal task waits for ALL
    # pending async tasks before it runs. So tasks that wait on another domain
    # must come last, or they would hold back independent ones listed after them.
    requested = set(wanted)

    def waits(name):
        return any(dep in requested for dep in DOMAINS[name].depends_on)

    # stable: independent domains first, original order kept. Sorting a copy,
    # because list.sort() makes the list look empty inside the key function.
    wanted = sorted(wanted, key=waits)
    tasks = {}

    for name in wanted:
        domain = DOMAINS[name]
        needs = [tasks[dep] for dep in domain.depends_on if dep in tasks]

        task = domain.make_task(agents[name], ticket, context=needs or None)
        task.async_execution = not needs
        tasks[name] = task

    return tasks
