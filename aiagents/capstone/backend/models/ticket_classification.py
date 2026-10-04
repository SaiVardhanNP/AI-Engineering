from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["billing", "account", "technical", "clarify", "other"]


class TicketClassification(BaseModel):
    categories: list[Category] = Field(
        min_length=1,
        description=(
            "Every domain the ticket involves. Use ['clarify'] alone for greetings, thanks, or messages "
            "too vague to investigate. Use ['other'] alone only if it fits none of the others."
        ),
    )
    reason: str = Field(description="One sentence explaining the choice")
    wants_action: bool = Field(
        default=False,
        description=(
            "True when the customer asks us to DO something we cannot do ourselves, such as refund a "
            "payment, cancel or change a plan, or delete data. False when they only ask a question "
            "or report a problem."
        ),
    )
    reply: str | None = Field(
        default=None,
        description=(
            "Only when categories is ['clarify']: a short friendly reply (under 40 words) that greets or "
            "thanks the customer and asks what they need help with. It must not state any fact about "
            "their account and must not mention any number."
        ),
    )
