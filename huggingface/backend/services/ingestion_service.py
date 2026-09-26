import hashlib
from collections import defaultdict
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class IngestionService:
    def __init__(self, vector_store, upload_dir):
        self.vector_store = vector_store
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    def ingest(self, filename, content):
        doc_id = hashlib.sha256(content).hexdigest()[:16]

        if self.vector_store.get(where={"doc_id": doc_id}, limit=1)["ids"]:
            return {"doc_id": doc_id, "status": "already_indexed"}

        path = self.upload_dir / f"{doc_id}.pdf"
        path.write_bytes(content)

        pages = PyPDFLoader(str(path)).load()
        chunks = self.splitter.split_documents(pages)

        for chunk in chunks:
            chunk.metadata["doc_id"] = doc_id
            chunk.metadata["source"] = filename

        self.vector_store.add_documents(chunks)

        return {
            "doc_id": doc_id,
            "status": "ingested",
            "pages": len(pages),
            "chunks": len(chunks),
        }

    def list_documents(self):
        chunk_counts = defaultdict(int)
        filenames = {}

        for metadata in self.vector_store.get()["metadatas"]:
            chunk_counts[metadata["doc_id"]] += 1
            filenames[metadata["doc_id"]] = metadata["source"]

        return [
            {"doc_id": doc_id, "filename": filenames[doc_id], "chunks": count}
            for doc_id, count in chunk_counts.items()
        ]
