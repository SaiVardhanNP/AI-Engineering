from typing import Literal
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    category: Literal["billing", "technical", "sales", "general"] = Field(
        description="Specifies the category of the Ticket"
    )
    priority: Literal["low", "medium", "high"] = Field(
        description="specifies the priority of the ticket"
    )
    summary: str = Field(description="specifies the summary of the ticket")


class SummarizeInput(BaseModel):
    text: str
    tone: Literal["professional", "casual"]
    length: Literal["short", "medium", "long"]
    persona: Literal["software_engineer", "technical_writer", "customer_support"]



class RewriteInput(BaseModel):
    text: str
    tone: Literal["professional", "friendly"]
    persona: Literal["software_engineer", "technical_writer", "customer_support"]
