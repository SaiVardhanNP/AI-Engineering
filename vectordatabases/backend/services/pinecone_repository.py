from pinecone import Pinecone
from config import settings


class PineconeRepository:
    def __init__(self):
        self.client = Pinecone(api_key=settings.pinecone_api_key)
        self.index = self.client.Index(settings.pinecone_index_name)

    def has_namespace(self, video_id):
        stats = self.index.describe_index_stats()
        namespace = stats.namespaces.get(video_id)
        return bool(namespace and namespace.vector_count > 0)

    def upsert_chunk(self, chunk, embedding, video_id, chunk_id):
        self.index.upsert(
            vectors=[
                {
                    "id": f"{video_id}#chunk-{chunk_id:04d}",
                    "values": embedding,
                    "metadata": {
                        "video_id": video_id,
                        "text": chunk["text"],
                        "start": chunk["start"],
                        "end": chunk["end"],
                    },
                }
            ],
            namespace=video_id,
        )

    def upsert_chunks(self, chunks, embeddings, video_id):
        self.index.upsert(
            vectors=[
                {
                    "id": f"{video_id}#chunk-{chunk_id:04d}",
                    "values": embedding,
                    "metadata": {
                        "video_id": video_id,
                        "text": chunk["text"],
                        "start": chunk["start"],
                        "end": chunk["end"],
                    },
                }
                for chunk_id, (chunk, embedding) in enumerate(
                    zip(chunks, embeddings), start=1
                )
            ],
            namespace=video_id,
        )

    def query(self, query_embedding, video_id, top_k=3):
        return self.index.query(
            vector=query_embedding,
            include_metadata=True,
            top_k=top_k,
            namespace=video_id,
        )

    def search(self, query_embedding, video_id, top_k=3):
        return [
            {
                "id": match["id"],
                "text": match.metadata["text"],
                "start": self._format_timestamp(match.metadata["start"]),
                "end": self._format_timestamp(match.metadata["end"]),
                "score": match["score"],
            }
            for match in self.index.query(
                vector=query_embedding,
                include_metadata=True,
                top_k=top_k,
                namespace=video_id,
            ).matches
        ]

    def _format_timestamp(self, seconds):
        total_seconds = int(seconds)
        minutes = total_seconds // 60
        secs = total_seconds % 60
        return f"{minutes:02d}:{secs:02d}"