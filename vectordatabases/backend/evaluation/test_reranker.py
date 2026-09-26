from services.embedding_service import EmbeddingService
from services.pinecone_repository import PineconeRepository
from services.bm25_repository import BM25Repository
from services.rrf_fusion import RRFFusion
from services.hybrid_retriever import HybridRetriever
from services.reranker import Reranker
from services.query_rewriter import QueryRewriter

video_id = "ZHCB09O6zUk"

embedding_service = EmbeddingService()
pinecone_repository = PineconeRepository()
bm25_repository = BM25Repository()
query_rewriter= QueryRewriter()

hybrid_retriever = HybridRetriever(
    embedding_service=embedding_service,
    pinecone_repository=pinecone_repository,
    bm25_repository=bm25_repository,
    rrf_fusion=RRFFusion(),
    reranker=Reranker(),
    query_rewriter=query_rewriter
)

question = "What game show did IBM Watson play in 2011?"

results = hybrid_retriever.search(
    question,
    video_id=video_id,
)

for rank, result in enumerate(results, start=1):
    print(f"\n--- Rank {rank} ---")
    print("ID:", result["id"])
    print("RRF Score:", result["score"])
    print("Rerank Score:", result["rerank_score"])
    print("Text:", result["text"])