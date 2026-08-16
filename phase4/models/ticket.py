from pydantic import BaseModel
from typing import Literal


class TicketInput(BaseModel):
    ticket: str


class TicketClassification(BaseModel):
    department: Literal["billing", "technical", "sales", "general"]
    priority: Literal["low", "medium", "high"]
    sentiment: Literal["positive", "neutral", "negative"]
