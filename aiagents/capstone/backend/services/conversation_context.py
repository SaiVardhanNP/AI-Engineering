MAX_CHARS_PER_MESSAGE = 400


def _clip(text):
    text = " ".join((text or "").split())
    return text if len(text) <= MAX_CHARS_PER_MESSAGE else text[: MAX_CHARS_PER_MESSAGE - 3] + "..."


def frame_ticket(message, turns):
    """The text the agents read as "the ticket".

    With no history it is just the message. With history it is the latest
    message under a short summary of the recent turns, so that "still not
    fixed" or "i was asking about that order" can be understood. The earlier
    lines are labelled as context only: the customer's own claims and the
    assistant's earlier replies are not evidence, only the findings are.
    """
    if not turns:
        return message

    lines = ["Conversation so far (context only, not verified facts):"]

    for turn in turns:
        lines.append("Customer: " + _clip(turn["message"]))
        if turn.get("reply"):
            lines.append("Assistant: " + _clip(turn["reply"]))
        if turn.get("human_reply"):
            lines.append("Support team: " + _clip(turn["human_reply"]))

    lines.append("")
    lines.append("Latest customer message: " + message)

    return "\n".join(lines)


def customer_words(message, turns):
    """Everything the customer has written in this conversation. A reply may
    repeat a number from here, because the customer typed it themselves."""
    return " ".join([turn["message"] for turn in turns or []] + [message])
