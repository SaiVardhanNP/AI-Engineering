class KnowledgeService:
    """Retrieval-only access to a company knowledge base.

    Returns ranked evidence chunks. It does not call an LLM, so the agent
    calling it decides how to reason over the evidence.
    """

    def __init__(self, retriever):
        self.retriever = retriever

    def search(self, question, kb_id, top_k=3):
        results = self.retriever.search(
            question=question,
            kb_id=kb_id,
            final_k=top_k,
        )

        return [
            {
                "id": result["id"],
                "title": result["title"],
                "section": result["section"],
                "url": result["url"],
                "text": result["text"],
                "rerank_score": result["rerank_score"],
            }
            for result in results
        ]
