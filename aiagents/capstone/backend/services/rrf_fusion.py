class RRFFusion:
    def __init__(self, k=60):
        self.k = k

    def fuse(self, result_lists, top_k=5):
        scores = {}
        documents = {}

        for results in result_lists:
            for rank, result in enumerate(results, start=1):
                document_id = result["id"]

                scores[document_id] = (
                    scores.get(document_id, 0)
                    + 1 / (self.k + rank)
                )

                if document_id not in documents:
                    documents[document_id] = result
                elif "_embedding" in result:
                    documents[document_id]["_embedding"] = (
                        result["_embedding"]
                    )

        ranked_ids = sorted(
            scores,
            key=scores.get,
            reverse=True,
        )[:top_k]

        return [
            {
                **documents[document_id],
                "score": scores[document_id],
            }
            for document_id in ranked_ids
        ]