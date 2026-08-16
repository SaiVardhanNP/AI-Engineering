from pydantic import BaseModel
from typing import Literal


class ToneInput(BaseModel):
    text: str
    tone: Literal["professional", "casual", "friendly"]
