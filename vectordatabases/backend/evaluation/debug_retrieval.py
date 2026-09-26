from services.embedding_service import EmbeddingService
from services.pinecone_repository import PineconeRepository
from services.bm25_repository import BM25Repository
from services.rrf_fusion import RRFFusion
from services.hybrid_retriever import HybridRetriever
from services.reranker import Reranker
from services.mmr import MMR
from services.query_rewriter import QueryRewriter


video_id = "ZHCB09O6zUk"

question = "How did expert systems differ from later machine learning?"


embedding_service = EmbeddingService()

pinecone_repository = PineconeRepository()

bm25_repository = BM25Repository()

mmr = MMR(
    lambda_param=0.5,
)

query_rewriter= QueryRewriter()

hybrid_retriever = HybridRetriever(
    embedding_service=embedding_service,
    pinecone_repository=pinecone_repository,
    bm25_repository=bm25_repository,
    rrf_fusion=RRFFusion(),
    reranker=Reranker(),
    mmr=mmr,
    query_rewriter=query_rewriter
)


results = hybrid_retriever.debug_search(
    question=question,
    video_id=video_id,
    candidate_k=20,
    final_k=3,
)


print("\n========== VECTOR TOP 20 ==========")

for rank, result in enumerate(
    results["vector"],
    start=1,
):
    print(f"\n--- Rank {rank} ---")
    print("ID:", result["id"])
    print("Vector Score:", result["score"])
    print("Text:", result["text"])


print("\n========== BM25 TOP 20 ==========")

for rank, result in enumerate(
    results["bm25"],
    start=1,
):
    print(f"\n--- Rank {rank} ---")
    print("ID:", result["id"])
    print("BM25 Score:", result["score"])
    print("Text:", result["text"])


print("\n========== RRF TOP 20 ==========")

for rank, result in enumerate(
    results["rrf"],
    start=1,
):
    print(f"\n--- Rank {rank} ---")
    print("ID:", result["id"])
    print("RRF Score:", result["score"])
    print("Text:", result["text"])


print("\n========== RERANKER TOP 10 ==========")

for rank, result in enumerate(
    results["reranked"],
    start=1,
):
    print(f"\n--- Rank {rank} ---")
    print("ID:", result["id"])
    print("Rerank Score:", result["rerank_score"])
    print("Has Embedding:", "_embedding" in result)
    print("Text:", result["text"])


print("\n========== MMR TOP 3 ==========")

for rank, result in enumerate(
    results["mmr"],
    start=1,
):
    print(f"\n--- Rank {rank} ---")
    print("ID:", result["id"])
    print("Rerank Score:", result["rerank_score"])
    print("Text:", result["text"])