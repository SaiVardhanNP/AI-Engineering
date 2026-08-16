from fastapi import APIRouter, Depends
from models.summarization import SummarizationInput, SummaryOutput
from prompts.summarization import SummarizationPrompt
from models.generate_request import GenerateRequest
from api.dependencies import get_pipeline
from typing import Annotated
from pipelines.ai_pipeline import AIPipeline

router = APIRouter()


@router.post("/summarize")
def summarize(
    request: SummarizationInput,
    pipeline: Annotated[AIPipeline, Depends(get_pipeline)],
):

    prompt = SummarizationPrompt().build_prompt(request)

    response = pipeline.generate(
        GenerateRequest(prompt=prompt), response_model=SummaryOutput
    )

    return response
