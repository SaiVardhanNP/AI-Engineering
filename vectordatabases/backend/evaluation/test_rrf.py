from services.rrf_fusion import RRFFusion


vector_results = [
    {"id": "chunk_22", "text": "Watson...", "score": 0.91},
    {"id": "chunk_30", "text": "Machine learning...", "score": 0.89},
    {"id": "chunk_26", "text": "Watson...", "score": 0.87},
    {"id": "chunk_10", "text": "Deep Blue...", "score": 0.85},
    {"id": "chunk_25", "text": "Watson...", "score": 0.83},
]

bm25_results = [
    {"id": "chunk_22", "text": "Watson...", "score": 9.43},
    {"id": "chunk_26", "text": "Watson...", "score": 6.82},
    {"id": "chunk_25", "text": "Watson...", "score": 6.64},
    {"id": "chunk_27", "text": "Jeopardy...", "score": 5.57},
    {"id": "chunk_5", "text": "Lisp...", "score": 5.39},
]


rrf = RRFFusion()

results = rrf.fuse(
    [vector_results, bm25_results],
    top_k=5,
)

for rank, result in enumerate(results, start=1):
    print(
        f"Rank {rank}: "
        f"{result['id']} "
        f"score={result['score']}"
    )