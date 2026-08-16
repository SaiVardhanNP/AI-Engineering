from pydantic import BaseModel


class CodeGenerationInput(BaseModel):
    language: str
    task: str
