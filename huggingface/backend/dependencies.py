from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import ChatHuggingFace, HuggingFaceEmbeddings, HuggingFacePipeline
from transformers import pipeline

from services.chat_service import ChatService
from services.ingestion_service import IngestionService
from services.model_registry import ModelRegistry

BASE_DIR = Path(__file__).parent

load_dotenv(BASE_DIR / ".env")


@lru_cache
def get_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return Chroma(
        collection_name="documents",
        embedding_function=embeddings,
        persist_directory=str(BASE_DIR / "chroma_db"),
    )


@lru_cache
def get_llm():
    pipe = pipeline(
        "text-generation",
        model="google/gemma-3-1b-it",
        max_new_tokens=150,
        return_full_text=False,
    )

    return ChatHuggingFace(llm=HuggingFacePipeline(pipeline=pipe))


@lru_cache
def get_ingestion_service():
    return IngestionService(get_vector_store(), BASE_DIR / "uploads")


@lru_cache
def get_model_registry():
    return ModelRegistry(get_llm)


@lru_cache
def get_chat_service():
    return ChatService(get_vector_store(), get_model_registry())
