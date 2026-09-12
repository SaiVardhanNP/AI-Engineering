from google import genai
from config import settings
from google.genai import types


class EmbeddingService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = "gemini-embedding-001"

    def embed_query(self, text: str):
        result = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )

        return result.embeddings[0].values

    def embed_documents(self, texts: list[str]):
        result = self.client.models.embed_content(
            model=self.model,
            contents=texts,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )

        return [embedding.values for embedding in result.embeddings]
