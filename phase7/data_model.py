from pydantic import BaseModel


class Document(BaseModel):
    id: str
    text: str


class SearchResult(BaseModel):
    document_id: str
    text: str
    score: float
