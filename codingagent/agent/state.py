from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class CodingAgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    task_status: str
    test_attempts: int
