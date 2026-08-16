from pydantic import BaseModel
from typing import Literal


class SummarizationInput(BaseModel):
    text: str
    length: Literal["short", "medium", "long"]

class SummaryOutput(BaseModel):
    title: str
    bullets: list[str]