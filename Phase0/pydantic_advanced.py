from pydantic import BaseModel, ValidationError, Field
from typing import Literal


class Message(BaseModel):
    role: Literal["User", "Assistant"]
    content: str


class ChatRequest(BaseModel):
    model: str
    temperature: int = 0.4
    max_tokens: int = Field(gt=0, le=4096)
    system_prompt: str | None = None
    messages: list[Message]


try:
    request = ChatRequest(
        model="GPT-5",
        temperature=1,
        max_tokens="4096",
        messages=[
            {"role": "User", "content": "Hey there!"},
            {"role": "Assistant", "content": "Hello! how can i help you?"},
        ],
    )
except ValidationError as e:
    print(e)

msg_contents = [msg.content for msg in request.messages]

for msg in msg_contents:
    print(msg)

print(type(request.messages[0]))
