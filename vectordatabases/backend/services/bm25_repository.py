from pathlib import Path

from services.bm25_retrieval import BM25Retriever


class BM25Repository:
    def __init__(self, storage_dir="storage/bm25"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(self, video_id, bm25_retriever):
        path = self.storage_dir / f"{video_id}.pkl"

        bm25_retriever.save(path)

    def get(self, video_id):
        path = self.storage_dir / f"{video_id}.pkl"

        if not path.exists():
            return None

        return BM25Retriever.load(path)