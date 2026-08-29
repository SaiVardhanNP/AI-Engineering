from google import genai
from config import settings
import numpy as np
from similarity_demo import cosine_similarity

client = genai.Client(api_key=settings.gemini_api_key)

sentences = [
    "I built a FastAPI backend.",
    "I created a Python API service.",
    "I cooked biryani for dinner.",
]

results = [
    client.models.embed_content(model="gemini-embedding-2", contents=sentence)
    for sentence in sentences
]

embeddings = [np.array(result.embeddings[0].values) for result in results]

print(cosine_similarity(embeddings[0], embeddings[1]))
print(cosine_similarity(embeddings[0], embeddings[2]))
print(cosine_similarity(embeddings[1], embeddings[2]))
