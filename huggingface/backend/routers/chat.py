from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from dependencies import get_chat_service
from services.chat_service import DocumentNotFound

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    doc_id: str
    question: str
    session_id: Optional[str] = None


class Source(BaseModel):
    page: Optional[int] = None
    text: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[Source]


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, service=Depends(get_chat_service)):
    try:
        return service.answer(
            request.doc_id, request.question, request.session_id
        )
    except DocumentNotFound:
        raise HTTPException(status_code=404, detail="Document not found")


@router.get("/{session_id}/history")
def get_history(session_id: str, service=Depends(get_chat_service)):
    return service.get_history(session_id)


@router.delete("/{session_id}/history", status_code=204)
def clear_history(session_id: str, service=Depends(get_chat_service)):
    service.clear_history(session_id)
