from services.embedding_service import EmbeddingService
from services.pinecone_repository import PineconeRepository
from services.bm25_repository import BM25Repository
from services.rrf_fusion import RRFFusion
from services.hybrid_retriever import HybridRetriever
from services.reranker import Reranker
from services.mmr import MMR
from services.query_rewriter import QueryRewriter
from services.rag_service import RAGService
from geminiClient import client


embedding_service = EmbeddingService()
pinecone_repository = PineconeRepository()
bm25_repository = BM25Repository()

query_rewriter = QueryRewriter()

mmr = MMR(
    lambda_param=0.5,
)

hybrid_retriever = HybridRetriever(
    embedding_service=embedding_service,
    pinecone_repository=pinecone_repository,
    bm25_repository=bm25_repository,
    rrf_fusion=RRFFusion(),
    reranker=Reranker(),
    mmr=mmr,
    query_rewriter=query_rewriter,
)

rag_service = RAGService(
    retriever=hybrid_retriever,
    llm_client=client,
)