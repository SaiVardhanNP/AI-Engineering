from pydantic import BaseModel
from typing import Literal


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ConversationContext(BaseModel):
    system_prompt: str
    summary: str
    recent_messages: list[Message]
    retrieved_memory: list[str]
    current_question: str


def build_context(data: ConversationContext) -> str:

    sections = [
        "System:",
        data.system_prompt,
        "",
        "Conversation Summary: ",
        data.summary,
        "",
        "Recent Messages: ",
        "",
    ]

    for msg in data.recent_messages:
        sections.append(f"{msg.role.capitalize()}:\n {msg.content}")
    sections.append("")
    sections.append("Retrieved Memory: ")
    sections.append("")

    for i, memory in enumerate(data.retrieved_memory, start=1):
        sections.append(f"Memory {i}\n{memory}")
    sections.append("")
    sections.append("Question: ")
    sections.append(data.current_question)

    return "\n".join(sections)


result = build_context(
    ConversationContext(
        system_prompt="You are helpful AI assistant",
        summary="User is learning AI Engineering.",
        recent_messages=[
            Message(role="user", content="Explain Pydantic."),
            Message(
                role="assistant",
                content="Pydantic is a data validation library that uses Python type hints.",
            ),
            Message(role="user", content="Explain Field in Pydantic."),
            Message(
                role="assistant",
                content="Field is used to provide metadata and validation constraints.",
            ),
            Message(role="user", content="Explain ValidationError."),
        ],
        retrieved_memory=[
            "User prefers Python.",
            "User is a full stack TypeScript developer.",
            "User wants to become a Full Stack AI Engineer.",
        ],
        current_question="How does Pydantic compare to dataclasses?",
    )
)
print(result)
