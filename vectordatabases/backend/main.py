from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.transcript_service import TranscriptService
from services.embedding_service import EmbeddingService
from services.pinecone_repository import PineconeRepository
from services.ingestion_service import IngestionService
from services.rag_service import RAGService
from geminiClient import client


app = FastAPI(title="YouTube RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

transcript_service = TranscriptService()
embedding_service = EmbeddingService()
pinecone_repository = PineconeRepository()

ingestion_service = IngestionService(
    transcript_service=transcript_service,
    embedding_service=embedding_service,
    pinecone_repository=pinecone_repository,
)

rag_service = RAGService(
    embedding_service=embedding_service,
    pinecone_repository=pinecone_repository,
    llm_client=client,
)


class IngestRequest(BaseModel):
    video_id: str


class IngestResponse(BaseModel):
    video_id: str
    status: str


class QueryRequest(BaseModel):
    video_id: str
    question: str
    top_k: int = Field(default=3, ge=1, le=10)


class Source(BaseModel):
    start: str
    end: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest):
    try:
        status = ingestion_service.ingest(request.video_id)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return IngestResponse(video_id=request.video_id, status=status)


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        result = rag_service.ask(
            question=request.question,
            video_id=request.video_id,
            top_k=request.top_k,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return QueryResponse(**result)
