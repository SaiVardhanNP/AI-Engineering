import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODEL_NAME = "gemini-3.5-flash-lite"


def get_llm() -> ChatGoogleGenerativeAI:
    # The library defaults to GOOGLE_API_KEY, but our .env uses GEMINI_API_KEY.
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
