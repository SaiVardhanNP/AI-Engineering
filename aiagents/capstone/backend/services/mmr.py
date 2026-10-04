import numpy as np


class MMR:
    def __init__(self, lambda_param=0.7):
        self.lambda_param = lambda_param

    def select(
        self,
        query_embedding,
        results,
        top_k=3,
    ):
        if len(results) <= top_k:
            return results

        document_embeddings = np.array([
            result["_embedding"]
            for result in results
        ])

        query_embedding = np.array(query_embedding)

        selected = []
        remaining = list(range(len(results)))

        while len(selected) < top_k:
            best_index = None
            best_score = float("-inf")

            for index in remaining:
                relevance = self._cosine_similarity(
                    query_embedding,
                    document_embeddings[index],
                )

                if not selected:
                    diversity = 0
                else:
                    diversity = max(
                        self._cosine_similarity(
                            document_embeddings[index],
                            document_embeddings[selected_index],
                        )
                        for selected_index in selected
                    )

                mmr_score = (
                    self.lambda_param * relevance
                    - (1 - self.lambda_param) * diversity
                )

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_index = index

            selected.append(best_index)
            remaining.remove(best_index)

        return [
            results[index]
            for index in selected
        ]

    def _cosine_similarity(self, a, b):
        denominator = (
            np.linalg.norm(a) *
            np.linalg.norm(b)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(a, b) / denominator
        )