from config import settings
from google import genai

client = genai.Client(api_key=settings.gemini_api_key)

sentences = ["I built a FastAPI backend.", "I cooked biryani for dinner."]

results = [
    (client.models.embed_content(model="gemini-embedding-2", contents=sentence))
    for sentence in sentences
]

for result in results:
    print(result.embeddings)
    embedding = result.embeddings[0].values
    print("Dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])
