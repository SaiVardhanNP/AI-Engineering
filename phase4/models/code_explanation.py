from pydantic import BaseModel
from typing import Literal


class CodeExplanationInput(BaseModel):
    code: str
    audience: Literal["beginner", "intermediate", "senior"]


class CodeExplanationOutput(BaseModel):
    summary: str
    explanation: str
    complexity: str
