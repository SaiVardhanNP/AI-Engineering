from pinecone import Pinecone
from config import settings


class PineconeRepository:
    def __init__(self):
        self.client = Pinecone(api_key=settings.pinecone_api_key)
        self.index = self.client.Index(settings.pinecone_index_name)

    def has_namespace(self, kb_id):
        stats = self.index.describe_index_stats()
        namespace = stats.namespaces.get(kb_id)
        return bool(namespace and namespace.vector_count > 0)

    def vector_count(self, kb_id):
        stats = self.index.describe_index_stats()
        namespace = stats.namespaces.get(kb_id)
        return namespace.vector_count if namespace else 0

    def upsert_chunks(self, chunks, embeddings, kb_id, start_id=1, batch_size=100):
        # start_id lets a resumed ingest continue the same chunk numbering,
        # which must match the ids BM25 generates (position in the chunk list + 1)
        vectors = [
            {
                "id": f"{kb_id}#chunk-{chunk_id:04d}",
                "values": embedding,
                "metadata": {
                    "kb_id": kb_id,
                    "text": chunk["text"],
                    "title": chunk["title"],
                    "section": chunk["section"],
                    "url": chunk["url"],
                },
            }
            for chunk_id, (chunk, embedding) in enumerate(
                zip(chunks, embeddings),
                start=start_id,
            )
        ]

        for start in range(0, len(vectors), batch_size):
            self.index.upsert(
                vectors=vectors[start:start + batch_size],
                namespace=kb_id,
            )

    def search(self, query_embedding, kb_id, top_k=3):
        response = self.index.query(
            vector=query_embedding,
            include_metadata=True,
            include_values=True,
            top_k=top_k,
            namespace=kb_id,
        )

        return [
            {
                "id": match["id"],
                "text": match.metadata["text"],
                "title": match.metadata["title"],
                "section": match.metadata["section"],
                "url": match.metadata["url"],
                "score": match["score"],
                "_embedding": match["values"],
            }
            for match in response.matches
        ]

    def fetch_embeddings(self, ids, kb_id):
        response = self.index.fetch(
            ids=ids,
            namespace=kb_id,
        )
        return {
            vector_id: vector["values"]
            for vector_id, vector in response.vectors.items()
        }
