from pydantic import BaseModel, Field


class Answer(BaseModel):
    answer: str = Field(description="The answer to the question")
    confidence: float = Field(description="confidence in the answer from 0 to 1")
