import argparse
import sys
from pathlib import Path

# allow `python scripts/ingest_docs.py` from the backend folder
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.bm25_repository import BM25Repository
from services.document_loader import DocumentLoader
from services.embedding_service import EmbeddingService
from services.ingestion_service import IngestionService
from services.pinecone_repository import PineconeRepository


def main():
    parser = argparse.ArgumentParser(description="Ingest a docs folder into a knowledge base")
    parser.add_argument("--kb-id", required=True, help="knowledge base name, e.g. supabase")
    parser.add_argument("--docs-dir", required=True, help="folder with .md/.mdx files")
    parser.add_argument("--base-url", default="", help="public docs URL used to build citation links")
    args = parser.parse_args()

    ingestion_service = IngestionService(
        document_loader=DocumentLoader(base_url=args.base_url),
        embedding_service=EmbeddingService(),
        pinecone_repository=PineconeRepository(),
        bm25_repository=BM25Repository(),
    )

    print(ingestion_service.ingest(args.kb_id, args.docs_dir))


if __name__ == "__main__":
    main()
