import numpy as np
from langchain_core.documents import Document


class MMR:

    def __init__(
        self,
        embeddings,
        lambda_mult: float = 0.5,
        top_k: int = 3,
    ):
        self.embeddings = embeddings
        self.lambda_mult = lambda_mult
        self.top_k = top_k

    @staticmethod
    def cosine_similarity(a, b) -> float:
        return np.dot(a, b) / (
            np.linalg.norm(a) * np.linalg.norm(b)
        )

    def select(
        self,
        query: str,
        documents: list[Document],
    ) -> list[Document]:

        if not documents:
            return []

        if len(documents) <= self.top_k:
            return documents

        query_embedding = np.array(
            self.embeddings.embed_query(query)
        )

        document_embeddings = [
            np.array(
                self.embeddings.embed_query(
                    document.page_content
                )
            )
            for document in documents
        ]

        selected = []
        remaining = list(range(len(documents)))

        # First document = most relevant to query
        query_scores = [
            self.cosine_similarity(
                query_embedding,
                embedding
            )
            for embedding in document_embeddings
        ]

        first_index = int(np.argmax(query_scores))

        selected.append(first_index)
        remaining.remove(first_index)

        # Select remaining documents using MMR
        while remaining and len(selected) < self.top_k:

            mmr_scores = {}

            for candidate in remaining:

                relevance = self.cosine_similarity(
                    query_embedding,
                    document_embeddings[candidate]
                )

                diversity = max(
                    self.cosine_similarity(
                        document_embeddings[candidate],
                        document_embeddings[selected_index]
                    )
                    for selected_index in selected
                )

                mmr_score = (
                    self.lambda_mult * relevance
                    - (1 - self.lambda_mult) * diversity
                )

                mmr_scores[candidate] = mmr_score

            best_index = max(
                mmr_scores,
                key=mmr_scores.get
            )

            selected.append(best_index)
            remaining.remove(best_index)

        return [
            documents[index]
            for index in selected
        ]