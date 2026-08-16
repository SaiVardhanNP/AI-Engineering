from pydantic import BaseModel


class TranslationInput(BaseModel):
    text: str
    target_language: str
