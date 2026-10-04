from sentence_transformers import CrossEncoder


class Reranker:
    def __init__(
        self,
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        self.model = CrossEncoder(model_name)

    def rerank(self, question, results, top_k=5):
        pairs = [
            [question, result["text"]]
            for result in results
        ]

        scores = self.model.predict(pairs)

        ranked_results = sorted(
            zip(results, scores),
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            {
                **result,
                "rerank_score": float(score),
            }
            for result, score in ranked_results[:top_k]
        ]