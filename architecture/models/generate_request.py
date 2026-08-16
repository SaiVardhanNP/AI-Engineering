from pydantic import BaseModel
from typing import Optional
from models.message import Message


class ChatRequest(BaseModel):
    messages: list[Message]
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None


class GenerateRequest(BaseModel):
    prompt: str
    system_prompt: str | None = None
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
