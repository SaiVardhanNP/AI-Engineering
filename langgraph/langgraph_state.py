from typing import TypedDict


class SupportState(TypedDict):
    ticket: str
    category: str
    response: str


ticket = SupportState(
    ticket="I was charged twice for my subscription",
    category="billing",
    response="we will check with the team and let you know!",
)


def classify_ticket(state: SupportState):
    text = state["ticket"].lower()

    if "charged" in text or "refund" in text:
        return {"category": "billing"}
    if "password" in text or "login" in text:
        return {"category": "account"}
    return {"category": "technical"}


def draft_response(state: SupportState):
    if state["category"] == "billing":
        return {"response": "We'll check your charges and get back to you."}
    if state["category"] == "account":
        return {"response": "We'll help you get back into your account."}
    return {"response": "Our engineers will look into this."}


state = {
    "ticket": "I was charged twice",
    "category": "",
    "response": "",
}

state.update(classify_ticket(state))
state.update(draft_response(state))

print(state)
