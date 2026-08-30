from load_documents import load_documents
import numpy as np
from embedding_index import generate_embedding
from semantic_index import SemanticIndex

documents = load_documents("documents")

index = SemanticIndex(documents=documents)

results = index.search("How do I make chocolate cake?", top_k=5, min_score=0.7)

index.test()

# for result in results:
#     print(result.document_id, result.score, result.text)
