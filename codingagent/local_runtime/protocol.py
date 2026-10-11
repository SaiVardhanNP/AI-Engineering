from pydantic import BaseModel
from typing import Any


class ToolRequest(BaseModel):
    call_id: str
    tool_name: str
    arguments: dict[str, Any]


class ToolResult(BaseModel):
    call_id: str
    success: bool
    content: Any = None
    error: str | None = None
