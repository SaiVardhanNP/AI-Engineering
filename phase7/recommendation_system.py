import numpy as np
from geminiClient import client


def generate_embedding(document):
    result = client.models.embed_content(model="gemini-embedding-2", contents=document)
    return np.array(result.embeddings[0].values)


items = [
    "FastAPI backend development",
    "Advanced React frontend development",
    "Python asynchronous programming",
    "Docker and containerization",
    "Node.js API development",
]

user_interests = [
    "Python backend development",
    "Building REST APIs with Python",
]

user_embeddings = np.array(
    [generate_embedding(user_intrest) for user_intrest in user_interests]
)

user_vector = np.mean(user_embeddings, axis=0)

user_norm = np.linalg.norm(user_vector)

item_embeddings = [generate_embedding(item) for item in items]

item_matrix = np.array(item_embeddings)
item_norms = np.linalg.norm(item_matrix, axis=1)

dot_products = item_matrix @ user_vector

scores = dot_products / (item_norms * user_norm)

results = list(zip(items, scores))

results.sort(key=lambda x: x[1], reverse=True)

top_k = 3

for item, score in results[:top_k]:
    print(f"{score:.4f} - {item}")
