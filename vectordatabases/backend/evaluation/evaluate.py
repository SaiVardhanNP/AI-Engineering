from evaluation.dataset import EVALUATION_DATASET
from evaluation.ragas_evaluator import evaluate_context_metrics

from services.rag_service import RAGService
from services.pinecone_repository import PineconeRepository
from services.embedding_service import EmbeddingService
from services.rrf_fusion import RRFFusion
from services.hybrid_retriever import HybridRetriever
from services.reranker import Reranker
from services.bm25_repository import BM25Repository
from services.mmr import MMR
from services.query_rewriter import QueryRewriter

from geminiClient import client

import asyncio


def run_evaluation(rag_service, video_id):
    results = []

    for evaluation in EVALUATION_DATASET:
        rag_result = rag_service.ask_for_evaluation(
            evaluation["question"],
            video_id=video_id,
        )

        results.append(
            {
                "question": evaluation["question"],
                "answer": rag_result["answer"],
                "contexts": rag_result["contexts"],
                "reference": evaluation["reference"],
            }
        )

    return results


embedding_service = EmbeddingService()
pinecone_repository = PineconeRepository()
bm25_repository = BM25Repository()
mmr = MMR(
    lambda_param=0.5,
)
query_rewriter= QueryRewriter()

hybrid_retriever = HybridRetriever(
    embedding_service=embedding_service,
    pinecone_repository=pinecone_repository,
    bm25_repository=bm25_repository,
    rrf_fusion=RRFFusion(),
    reranker=Reranker(),
    mmr=mmr,
    query_rewriter=query_rewriter
)

rag_service = RAGService(
    retriever=hybrid_retriever,
    llm_client=client,
)


results = run_evaluation(
    rag_service,
    video_id="ZHCB09O6zUk",
)

scores = asyncio.run(evaluate_context_metrics(results))

for score in scores:
    print(score)
