import numpy as np
from geminiClient import client
from data_model import SearchResult, Document


class SemanticIndex:
    def __init__(self, documents: list[Document]):
        self.documents = documents
        self.document_embeddings = [
            self._generate_embedding(document.text) for document in self.documents
        ]

        self.document_matrix = np.array(self.document_embeddings)
        np.save("document_embeddings.npy", self.document_matrix)
        self.document_norms = np.linalg.norm(self.document_matrix, axis=1)

    def search(self, query, top_k=5, min_score=0.0) -> list[SearchResult]:

        query_embedding = self._generate_embedding(query)
        query_norm = np.linalg.norm(query_embedding)

        dot_products = self.document_matrix @ query_embedding

        scores = dot_products / (self.document_norms * query_norm)

        results = list(zip(self.documents, scores))

        results = [result for result in results if result[1] >= min_score]

        results.sort(key=lambda x: x[1], reverse=True)

        return [
            SearchResult(
                document_id=document.id, text=document.text, score=float(score)
            )
            for document, score in results[:top_k]
        ]

    def _generate_embedding(self, document):
        result = client.models.embed_content(
            model="gemini-embedding-2", contents=document
        )
        return np.array(result.embeddings[0].values)

    def test(self):
        loaded_matrix = np.load("document_embeddings.npy")
        print(loaded_matrix.shape)
        print(np.array_equal(self.document_matrix, loaded_matrix))
