from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document


class KeywordRetriever(BaseRetriever):
    documents: list[Document]

    def _get_relevant_documents(self, query):
        query_words = query.lower().split()

        results = []

        for document in self.documents:
            text = document.page_content.lower()
            if any(word in text for word in query_words):
                results.append(document)
        return results
