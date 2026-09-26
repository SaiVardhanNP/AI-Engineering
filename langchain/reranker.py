from sentence_transformers import CrossEncoder
from langchain_core.documents import Document


class CrossEncoderReranker:

    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(
        self,
        query: str,
        documents: list[Document]
    ) -> list[Document]:

        pairs = [
            (query, document.page_content)
            for document in documents
        ]

        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(scores, documents),
            key=lambda x: x[0],
            reverse=True
        )

        return [
            document
            for score, document in ranked
        ]