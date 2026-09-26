import pickle

from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self, chunks, video_id):
        self.chunks = chunks
        self.video_id = video_id

        tokenized_chunks = [
            self._tokenize(chunk["text"])
            for chunk in chunks
        ]

        self.bm25 = BM25Okapi(tokenized_chunks)

    def search(self, query, top_k=5):
        tokenized_query = self._tokenize(query)

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:top_k]

        return [
            {
                "id": f"{self.video_id}#chunk-{index + 1:04d}",
                "text": self.chunks[index]["text"],
                "start": self._format_timestamp(
                    self.chunks[index]["start"]
                ),
                "end": self._format_timestamp(
                    self.chunks[index]["end"]
                ),
                "score": float(scores[index]),
            }
            for index in ranked_indices
        ]

    def save(self, path):
        with open(path, "wb") as file:
            pickle.dump(self, file)

    @classmethod
    def load(cls, path):
        with open(path, "rb") as file:
            return pickle.load(file)

    def _tokenize(self, text):
        return text.lower().split()

    def _format_timestamp(self, seconds):
        total_seconds = int(seconds)

        minutes = total_seconds // 60
        secs = total_seconds % 60

        return f"{minutes:02d}:{secs:02d}"