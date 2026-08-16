from pydantic import BaseModel, field_validator, Field, ValidationError, model_validator
from typing import Literal


class Message(BaseModel):
    role: Literal["Assistant", "User"]
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, content: str):
        return content.strip()


class ChatRequest(BaseModel):
    model: str
    temperature: int = 0
    top_p: int
    messages: list[Message]
    system_prompt: str | None=None

    @model_validator(mode="after")
    def validate_settings(self):

        if self.temperature == 0 and not (self.top_p == 1):
            raise ValueError("Top-P cant be more than 1 if temperature is 0.")

        return self

    @field_validator("system_prompt")
    @classmethod
    def validate_prompt(cls, value: str):
        if len(value.strip()) == 0:
            raise ValueError("Prompt cannot be empty")
        return value


try:
    request = ChatRequest(
        model="GPT-5",
        top_p=1,
        messages=[
            {"role": "User", "content": "Hey there!"},
            {"role": "Assistant", "content": "Hello! how can i help you?"},
        ],
    )
    
    print(request.model_dump(exclude_none=True, exclude_defaults=True))

except ValidationError as e:
    print(e)
