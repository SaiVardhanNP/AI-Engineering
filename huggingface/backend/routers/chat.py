import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from dependencies import get_chat_service
from services.chat_service import DocumentNotFound
from services.model_registry import UnknownModel

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    doc_id: str
    question: str
    session_id: Optional[str] = None
    model: Optional[str] = None


class Source(BaseModel):
    page: Optional[int] = None
    text: str


class UsedModel(BaseModel):
    id: str
    label: str
    provider: str


class ChatResponse(BaseModel):
    session_id: str
    model: UsedModel
    answer: str
    sources: list[Source]


def redact(text):
    for name in ("GEMINI_API_KEY", "GROQ_API_KEY"):
        value = os.getenv(name)

        if value:
            text = text.replace(value, "***")

    return text[:300]


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, service=Depends(get_chat_service)):
    try:
        return service.answer(
            request.doc_id, request.question, request.session_id, request.model
        )
    except DocumentNotFound:
        raise HTTPException(status_code=404, detail="Document not found")
    except UnknownModel:
        raise HTTPException(status_code=400, detail="Unknown model")
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"The model call failed ({type(error).__name__}): {redact(str(error))}",
        )


@router.get("/{session_id}/history")
def get_history(session_id: str, service=Depends(get_chat_service)):
    return service.get_history(session_id)


@router.delete("/{session_id}/history", status_code=204)
def clear_history(session_id: str, service=Depends(get_chat_service)):
    service.clear_history(session_id)
