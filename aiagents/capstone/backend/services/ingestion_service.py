import time

from google.genai import errors

from services.bm25_retrieval import BM25Retriever


class IngestionService:
    def __init__(
        self,
        document_loader,
        embedding_service,
        pinecone_repository,
        bm25_repository,
        embed_batch_size=100,
        rate_limit_wait=30,
        max_retries=10,
    ):
        self.document_loader = document_loader
        self.embedding_service = embedding_service
        self.pinecone_repository = pinecone_repository
        self.bm25_repository = bm25_repository
        self.embed_batch_size = embed_batch_size
        self.rate_limit_wait = rate_limit_wait
        self.max_retries = max_retries

    def ingest(self, kb_id, docs_dir):
        chunks = self.document_loader.load_directory(docs_dir)

        # BM25 is cheap and local, so always rebuild it from the same chunks
        self.bm25_repository.save(
            kb_id,
            BM25Retriever(chunks=chunks, kb_id=kb_id),
        )

        # chunk ids are sequential and each batch is upserted as soon as it is
        # embedded, so the vectors already stored tell us where to resume
        done = self.pinecone_repository.vector_count(kb_id)

        if done >= len(chunks):
            return "already_indexed"

        for start in range(done, len(chunks), self.embed_batch_size):
            batch = chunks[start:start + self.embed_batch_size]

            embeddings = self._embed_with_retry([chunk["text"] for chunk in batch])

            self.pinecone_repository.upsert_chunks(
                batch,
                embeddings,
                kb_id=kb_id,
                start_id=start + 1,
            )

            print(f"indexed {min(start + len(batch), len(chunks))}/{len(chunks)}", flush=True)

        return f"ingested {len(chunks) - done} chunks"

    def _embed_with_retry(self, texts):
        for attempt in range(1, self.max_retries + 1):
            try:
                return self.embedding_service.embed_documents(texts)
            except errors.ClientError as error:
                if error.code != 429 or attempt == self.max_retries:
                    raise

                print(f"rate limited, waiting {self.rate_limit_wait}s (attempt {attempt})", flush=True)
                time.sleep(self.rate_limit_wait)
