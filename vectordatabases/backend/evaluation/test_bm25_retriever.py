from services.bm25_retrieval import BM25Retriever
from services.chunk_repository import ChunkRepository


video_id = "ZHCB09O6zUk"

chunk_repository = ChunkRepository()

chunks = chunk_repository.get(video_id)

bm25 = BM25Retriever(
    chunks=chunks,
    video_id=video_id,
)

results = bm25.search(
    "What game show did IBM Watson play in 2011?",
    top_k=5,
)

for rank, result in enumerate(results, start=1):
    print(f"\n--- Rank {rank} ---")
    print("ID:", result["id"])
    print("Score:", result["score"])
    print("Text:", result["text"])