import uuid

from langchain_community.retrievers import BM25Retriever
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.documents import Document
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from hybrid_retriever import HybridRetriever

PROMPT = PromptTemplate.from_template("""
Answer the question using only the provided context.
Each context passage has a number in square brackets. End every statement with the number of the passage it came from, like this: The course covers RAG systems [2] and agents [3].
Use the conversation history to understand follow-up questions.

Conversation history:
{history}

Context:
{context}

Question:
{question}

Answer:
""")


class DocumentNotFound(Exception):
    pass


class ChatService:
    def __init__(self, vector_store, models, candidate_k=5, top_k=3, history_window=6):
        self.vector_store = vector_store
        self.models = models
        self.candidate_k = candidate_k
        self.top_k = top_k
        self.bm25_cache = {}
        self.history_window = history_window
        self.histories = {}

    def _history(self, session_id):
        if session_id not in self.histories:
            self.histories[session_id] = InMemoryChatMessageHistory()

        return self.histories[session_id]

    def _bm25_retriever(self, doc_id):
        if doc_id not in self.bm25_cache:
            stored = self.vector_store.get(where={"doc_id": doc_id})

            if not stored["ids"]:
                raise DocumentNotFound(doc_id)

            documents = [
                Document(page_content=text, metadata=metadata)
                for text, metadata in zip(stored["documents"], stored["metadatas"])
            ]

            self.bm25_cache[doc_id] = BM25Retriever.from_documents(
                documents, k=self.candidate_k
            )

        return self.bm25_cache[doc_id]

    def _retriever(self, doc_id):
        vector_retriever = self.vector_store.as_retriever(
            search_kwargs={"k": self.candidate_k, "filter": {"doc_id": doc_id}}
        )

        return HybridRetriever(
            retrievers=[vector_retriever, self._bm25_retriever(doc_id)],
            weights=[0.5, 0.5],
            top_k=self.top_k,
        )

    def answer(self, doc_id, question, session_id=None, model_id=None):
        model = self.models.describe(model_id)
        chain = PROMPT | self.models.get(model["id"]) | StrOutputParser()

        session_id = session_id or str(uuid.uuid4())
        history = self._history(session_id)

        docs = self._retriever(doc_id).invoke(question)

        context = "\n\n".join(
            f"[{number}] {doc.page_content}"
            for number, doc in enumerate(docs, start=1)
        )

        recent = history.messages[-self.history_window:]

        answer = chain.invoke(
            {
                "history": get_buffer_string(recent) or "(none)",
                "context": context,
                "question": question,
            }
        ).strip()

        history.add_user_message(question)
        history.add_ai_message(answer)

        return {
            "session_id": session_id,
            "model": {"id": model["id"], "label": model["label"], "provider": model["provider"]},
            "answer": answer,
            "sources": [
                {"page": doc.metadata.get("page"), "text": doc.page_content}
                for doc in docs
            ],
        }

    def get_history(self, session_id):
        return [
            {"role": message.type, "content": message.content}
            for message in self._history(session_id).messages
        ]

    def clear_history(self, session_id):
        self.histories.pop(session_id, None)
