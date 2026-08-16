from pydantic import BaseModel


class ImproveWritingInput(BaseModel):
    text: str
