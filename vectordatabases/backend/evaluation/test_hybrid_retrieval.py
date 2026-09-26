from services.bm25_retrieval import BM25Retriever
from services.chunk_repository import ChunkRepository
from services.embedding_service import EmbeddingService
from services.pinecone_repository import PineconeRepository
from services.rrf_fusion import RRFFusion
from services.reranker import Reranker
from services.hybrid_retriever import HybridRetriever
from services.query_rewriter import QueryRewriter


video_id = "ZHCB09O6zUk"

chunk_repository = ChunkRepository()
chunks = chunk_repository.get(video_id)

bm25 = BM25Retriever(
    chunks=chunks,
    video_id=video_id,
)

embedding_service = EmbeddingService()
pinecone_repository = PineconeRepository()
rrf = RRFFusion()
rewriter = QueryRewriter()

hybrid = HybridRetriever(
    embedding_service=embedding_service,
    pinecone_repository=pinecone_repository,
    chunk_repository=chunk_repository,
    rrf_fusion=RRFFusion(),
    reranker=Reranker(),
    query_rewriter=rewriter
)

results = hybrid.search(
    "What game show did IBM Watson play in 2011?",
    video_id=video_id,
    top_k=5,
)

for rank, result in enumerate(results, start=1):
    print(f"\n--- Rank {rank} ---")
    print("ID:", result["id"])
    print("RRF Score:", result["score"])
    print("Text:", result["text"])
