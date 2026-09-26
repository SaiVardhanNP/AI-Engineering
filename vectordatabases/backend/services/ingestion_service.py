from services.bm25_retrieval import BM25Retriever


class IngestionService:
    def __init__(
        self,
        transcript_service,
        embedding_service,
        pinecone_repository,
        bm25_repository,
    ):
        self.transcript_service = transcript_service
        self.embedding_service = embedding_service
        self.pinecone_repository = pinecone_repository
        self.bm25_repository = bm25_repository

    def ingest(self, video_id):
        if self.pinecone_repository.has_namespace(video_id):
            return "already_indexed"

        transcript = self.transcript_service.fetch(video_id)

        segments = self.transcript_service.clean(transcript)

        chunks = self.transcript_service.chunk(segments)


        bm25_retriever = BM25Retriever(
            chunks=chunks,
            video_id=video_id,
        )

        self.bm25_repository.save(
            video_id,
            bm25_retriever,
        )

        embeddings = self.embedding_service.embed_documents(
            [chunk["text"] for chunk in chunks]
        )

        self.pinecone_repository.upsert_chunks(
            chunks,
            embeddings,
            video_id=video_id,
        )

        return "ingested"