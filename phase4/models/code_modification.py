from pydantic import BaseModel


class CodeModificationInput(BaseModel):
    code: str
    instruction: str
