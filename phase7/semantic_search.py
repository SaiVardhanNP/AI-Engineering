import numpy as np
from geminiClient import client


documents = [
    "FastAPI is a Python framework for building APIs.",
    "Express is a Node.js framework for building web servers.",
    "React is a JavaScript library for building user interfaces.",
    "Docker packages applications into portable containers.",
    "Embeddings represent text as numerical vectors.",
]

query = "How can I build an API using Python?"


class SemanticIndex:
    def __init__(self, documents):
        self.documents = documents

        document_embeddings = [
            self._generate_embeddings(document) for document in documents
        ]

        self.document_matrix = np.array(document_embeddings)

        self.document_norms = np.linalg.norm(self.document_matrix, axis=1)

    def search(self, query, top_k=3):
        query_embedding = self._generate_embeddings(query)
        query_norm = np.linalg.norm(query_embedding)

        dot_products = self.document_matrix @ query_embedding

        scores = dot_products / (self.document_norms * query_norm)

        results = list(zip(self.documents, scores))

        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def _generate_embeddings(self, document):
        result = client.models.embed_content(
            model="gemini-embedding-2", contents=document
        )
        return np.array(result.embeddings[0].values)


index = SemanticIndex(documents=documents)

results = index.search(query=query, top_k=2)

for document, score in results:
    print(f"{score:.4f} - {document}")

results = index.search("How do I build a frontend?", top_k=2)

print("\n\n\n")
for document, score in results:
    print(f"{score:.4f} - {document}")
