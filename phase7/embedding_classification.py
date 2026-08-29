import numpy as np
from geminiClient import client
from cosine_similarity import cosine_similarity


def generate_embedding(document):
    result = client.models.embed_content(model="gemini-embedding-2", contents=document)
    return np.array(result.embeddings[0].values)


categories = {
    "backend": [
        "FastAPI endpoint returns an error",
        "Node.js API is failing",
        "Database query in the backend is slow",
    ],
    "frontend": [
        "React component is not rendering",
        "CSS layout is broken",
        "Button click handler is not working",
    ],
    "devops": [
        "Docker container keeps crashing",
        "Kubernetes deployment failed",
        "CI pipeline is failing",
    ],
}

category_embeddings = {}

for category, examples in categories.items():
    category_embeddings[category] = [
        generate_embedding(example) for example in examples
    ]

text = "My FastAPI API endpoint returns a 500 error"

query_embedding = generate_embedding(text)


category_scores = {}

for category, embeddings in category_embeddings.items():
    scores = [cosine_similarity(embedding, query_embedding) for embedding in embeddings]

    category_scores[category] = scores

best_category_scores = {
    category: np.max(scores)
    for category, scores in category_scores.items()
}

print(best_category_scores)

prediction= max(best_category_scores,key=best_category_scores.get)

print(prediction)