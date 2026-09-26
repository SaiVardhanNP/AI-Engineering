from typing import List, Optional

from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.retrievers import BaseRetriever


class HybridRetriever(BaseRetriever):
    retrievers: List[BaseRetriever]
    weights: Optional[List[float]] = None
    top_k: int = 3

    def _get_relevant_documents(self, query, *, run_manager):
        ensemble = EnsembleRetriever(
            retrievers=self.retrievers,
            weights=self.weights,
        )

        return ensemble.invoke(query)[: self.top_k]
