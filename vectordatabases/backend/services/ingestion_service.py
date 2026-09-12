class IngestionService:
    def __init__(self, transcript_service, embedding_service, pinecone_repository):
        self.transcript_service = transcript_service
        self.embedding_service = embedding_service
        self.pinecone_repository = pinecone_repository

    def ingest(self, video_id):
        if self.pinecone_repository.has_namespace(video_id):
            return "already_indexed"

        transcript = self.transcript_service.fetch(video_id)

        segments = self.transcript_service.clean(transcript)

        chunks = self.transcript_service.chunk(segments)

        embeddings = self.embedding_service.embed_documents(
            [chunk["text"] for chunk in chunks]
        )

        self.pinecone_repository.upsert_chunks(
            chunks,
            embeddings,
            video_id=video_id,
        )

        return "ingested"
