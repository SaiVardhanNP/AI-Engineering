import asyncio

from services.embedding_service import EmbeddingService
from services.pinecone_repository import PineconeRepository
from services.bm25_repository import BM25Repository
from services.rrf_fusion import RRFFusion
from services.reranker import Reranker
from services.mmr import MMR
from services.query_rewriter import QueryRewriter
from services.hybrid_retriever import HybridRetriever

from evaluation.dataset import EVALUATION_DATASET
from evaluation.ragas_evaluator import evaluate_context_metrics


VIDEO_ID = "ZHCB09O6zUk"


def build_retriever():
    embedding_service = EmbeddingService()
    pinecone_repository = PineconeRepository()
    bm25_repository = BM25Repository()
    rrf_fusion = RRFFusion()
    reranker = Reranker()
    mmr = MMR(lambda_param=0.5)
    query_rewriter = QueryRewriter()

    return HybridRetriever(
        embedding_service=embedding_service,
        pinecone_repository=pinecone_repository,
        bm25_repository=bm25_repository,
        rrf_fusion=rrf_fusion,
        reranker=reranker,
        mmr=mmr,
        query_rewriter=query_rewriter,
    )


def collect_results(retriever):
    results = []

    for item in EVALUATION_DATASET:
        question = item["question"]
        reference = item["reference"]

        print("\n" + "=" * 80)
        print("QUESTION")
        print(question)

        debug = retriever.debug_search(
            question=question,
            video_id=VIDEO_ID,
            candidate_k=20,
            final_k=3,
        )

        contexts = [result["text"] for result in debug["mmr"]]

        result = {
            "question": question,
            "reference": reference,
            "contexts": contexts,
            "should_rewrite": debug["should_rewrite"],
            "rewritten_query": debug["rewritten_query"],
        }

        results.append(result)

        print("\nREWRITE DECISION")
        print("Should rewrite:", result["should_rewrite"])
        print("Rewritten query:", result["rewritten_query"])

        print("\nFINAL MMR CONTEXTS")

        for index, context in enumerate(contexts, start=1):
            print(f"\n[{index}]")
            print(context)

    return results


def print_rewrite_summary(results):
    print("\n")
    print("=" * 80)
    print("QUERY REWRITE SUMMARY")
    print("=" * 80)

    rewrite_count = 0

    for result in results:
        if result["should_rewrite"]:
            rewrite_count += 1

        print("\nQuestion:")
        print(result["question"])

        print("Should rewrite:")
        print(result["should_rewrite"])

        print("Rewritten query:")
        print(result["rewritten_query"])

    print("\n")
    print(f"Queries rewritten: {rewrite_count}/{len(results)}")


def print_ragas_scores(scores):
    print("\n")
    print("=" * 80)
    print("RAGAS RESULTS")
    print("=" * 80)

    total_precision = 0.0
    total_recall = 0.0

    for score in scores:
        precision = score["context_precision"]
        recall = score["context_recall"]

        total_precision += precision
        total_recall += recall

        print("\nQuestion:")
        print(score["question"])

        print(
            "Context Precision:",
            precision,
        )

        print(
            "Context Recall:",
            recall,
        )

    if scores:
        average_precision = total_precision / len(scores)

        average_recall = total_recall / len(scores)

        print("\n")
        print("=" * 80)
        print("AVERAGE")
        print("=" * 80)

        print(
            "Average Context Precision:",
            average_precision,
        )

        print(
            "Average Context Recall:",
            average_recall,
        )


async def main():
    retriever = build_retriever()

    print("\n")
    print("=" * 80)
    print("SELECTIVE QUERY REWRITE EVALUATION")
    print("=" * 80)

    results = collect_results(retriever)

    print_rewrite_summary(results)

    print("\n")
    print("Running RAGAS evaluation...")

    scores = await evaluate_context_metrics(results)

    print_ragas_scores(scores)


if __name__ == "__main__":
    asyncio.run(main())
