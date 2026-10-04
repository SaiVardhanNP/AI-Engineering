from services.reply_verifier import mentions_a_person


def handoff_reason(wants_action, duplicate_invoices):
    """Decide, from facts and not from a model's mood, whether a person must see
    this ticket. Returns the reason, or None when the assistant can finish alone.

    wants_action: the router saw the customer ask us to DO something (refund,
        cancel, change). The assistant cannot do those things itself.
    duplicate_invoices: invoices the database shows were charged more than once.
        Undoing a duplicate charge needs a person, whatever the customer asked.
    """
    reasons = []

    if wants_action:
        reasons.append("the customer asked for something only a person can do (a refund, cancellation or change)")
    if duplicate_invoices:
        reasons.append("a duplicate charge is on file for " + ", ".join(sorted(duplicate_invoices)))

    return "; ".join(reasons) or None


def check_handoff(draft, reason):
    """Problems if what the reply says about a person does not match reality.

    If a person must act, the customer has to be told. If nobody will follow up,
    the reply must not say anyone will, because that promise would be false.
    """
    if reason and not mentions_a_person(draft):
        return [
            "A person must take care of this (" + reason + "). The reply must say plainly that a team member "
            "will take care of it, without saying when."
        ]

    if not reason and mentions_a_person(draft):
        return [
            "The reply says a team member or review will follow up, but nobody will. Remove that, and make "
            "the reply answer the question completely."
        ]

    return []
