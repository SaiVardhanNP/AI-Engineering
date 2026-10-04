from functools import lru_cache

from services.bm25_repository import BM25Repository
from services.customer_data_service import CustomerDataService
from services.embedding_service import EmbeddingService
from services.hybrid_retriever import HybridRetriever
from services.knowledge_service import KnowledgeService
from services.mmr import MMR
from services.pinecone_repository import PineconeRepository
from services.query_rewriter import QueryRewriter
from services.reranker import Reranker
from services.rrf_fusion import RRFFusion
from services.conversation_store import ConversationStore
from services.ticket_store import TicketStore


@lru_cache
def get_data_service():
    return CustomerDataService()


@lru_cache
def get_knowledge_service():
    # built once: importing torch and loading the reranker takes about a minute
    return KnowledgeService(
        HybridRetriever(
            embedding_service=EmbeddingService(),
            pinecone_repository=PineconeRepository(),
            bm25_repository=BM25Repository(),
            rrf_fusion=RRFFusion(),
            reranker=Reranker(),
            mmr=MMR(),
            query_rewriter=QueryRewriter(),
        )
    )


@lru_cache
def get_ticket_store():
    return TicketStore()


@lru_cache
def get_conversation_store():
    return ConversationStore()
