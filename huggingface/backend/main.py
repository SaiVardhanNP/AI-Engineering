from contextlib import asynccontextmanager

from fastapi import FastAPI

from dependencies import get_chat_service, get_ingestion_service
from routers import chat, ingestion


@asynccontextmanager
async def lifespan(app):
    get_ingestion_service()
    get_chat_service()
    yield


app = FastAPI(title="Local RAG", lifespan=lifespan)

app.include_router(ingestion.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
