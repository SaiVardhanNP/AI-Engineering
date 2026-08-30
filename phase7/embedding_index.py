import numpy as np
from load_documents import load_documents
from geminiClient import client


def generate_embedding(text: str) -> np.ndarray:
    result = client.models.embed_content(model="gemini-embedding-2", contents=text)

    embedding = np.array(result.embeddings[0].values)

    return embedding
