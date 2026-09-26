from ragas.llms import llm_factory
from ragas.metrics.collections import ContextPrecision, ContextRecall

from config import settings
from openai import AsyncOpenAI


client = AsyncOpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)

evaluator_llm = llm_factory(
    "openai/gpt-oss-20b",
    provider="openai",
    client=client,
    max_tokens=4096,
)

context_precision = ContextPrecision(
    llm=evaluator_llm
)

context_recall = ContextRecall(
    llm=evaluator_llm
)


async def evaluate_context_metrics(results):
    answerable_results = [
        result
        for result in results
        if result["reference"] is not None
    ]

    scores = []

    for result in answerable_results:

        precision = await context_precision.ascore(
            user_input=result["question"],
            reference=result["reference"],
            retrieved_contexts=result["contexts"],
        )

        recall = await context_recall.ascore(
            user_input=result["question"],
            reference=result["reference"],
            retrieved_contexts=result["contexts"],
        )

        scores.append(
            {
                "question": result["question"],
                "context_precision": precision.value,
                "context_recall": recall.value,
            }
        )

    return scores