import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI

from dependencies import get_chat_service, get_ingestion_service, get_model_registry
from routers import chat, ingestion, models
from services.model_registry import LOCAL_ID


@asynccontextmanager
async def lifespan(app):
    get_ingestion_service()
    get_chat_service()

    threading.Thread(
        target=lambda: get_model_registry().get(LOCAL_ID),
        daemon=True,
    ).start()

    yield


app = FastAPI(title="Local RAG", lifespan=lifespan)

app.include_router(ingestion.router)
app.include_router(models.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok"}
