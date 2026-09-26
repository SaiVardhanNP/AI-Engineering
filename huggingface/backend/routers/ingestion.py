from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from dependencies import get_ingestion_service

router = APIRouter(prefix="/documents", tags=["ingestion"])


class IngestResponse(BaseModel):
    doc_id: str
    status: str
    pages: Optional[int] = None
    chunks: Optional[int] = None


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    chunks: int


@router.post("", response_model=IngestResponse)
def ingest_document(
    file: UploadFile = File(...),
    service=Depends(get_ingestion_service),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    return service.ingest(file.filename, file.file.read())


@router.get("", response_model=list[DocumentInfo])
def list_documents(service=Depends(get_ingestion_service)):
    return service.list_documents()


@router.get("/{doc_id}/file")
def get_document_file(doc_id: str, service=Depends(get_ingestion_service)):
    path = service.file_path(doc_id)

    if path is None:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path, media_type="application/pdf")
