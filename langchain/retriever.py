from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
class HybridRetriever(BaseRetriever):

    keyword_retriever: BaseRetriever
    vector_retriever: BaseRetriever
    reranker: object
    mmr: object
    top_k: int = 2

    def _get_relevant_documents(
        self,
        query: str
    ) -> list[Document]:

        vector_results = self.vector_retriever.invoke(query)
        keyword_results = self.keyword_retriever.invoke(query)

        scores = {}
        documents = {}

        k = 60

        for rank, document in enumerate(vector_results, start=1):
            doc_id = document.page_content

            scores[doc_id] = (
                scores.get(doc_id, 0)
                + 1 / (k + rank)
            )

            documents[doc_id] = document

        for rank, document in enumerate(keyword_results, start=1):
            doc_id = document.page_content

            scores[doc_id] = (
                scores.get(doc_id, 0)
                + 1 / (k + rank)
            )

            documents[doc_id] = document

        ranked_ids = sorted(
            scores,
            key=scores.get,
            reverse=True
        )

        candidates = [
            documents[doc_id]
            for doc_id in ranked_ids
        ]

        reranked = self.reranker.rerank(
            query,
            candidates
        )

        return self.mmr.select(
            query,
            reranked
        )