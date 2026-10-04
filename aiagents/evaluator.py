from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from rag_tool import SupportRAG

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.5-flash-lite"


class EvaluationResponse(BaseModel):
    relevant: bool = Field(
        description="Does the response address the customer's issue?"
    )
    faithful: bool = Field(
        description="Is every claim in the response supported by the retrieved context?"
    )
    complete: bool = Field(
        description="Does the response adequately address the whole issue?"
    )
    confidence: float = Field(
        ge=0, le=1, description="Evaluator confidence in this verdict, from 0 to 1"
    )
    feedback: str = Field(
        description="What should be fixed. Quote any unsupported claims. 'None' if nothing."
    )


def format_context(context: list[str]) -> str:
    return "\n".join(context) if context else "(none)"


def generator(ticket: str, context: list[str], extra_instructions: str = "") -> str:
    prompt = f"""You are a customer support agent. Write a reply to the ticket below.

Ticket:
{ticket}

Retrieved context:
{format_context(context)}

Use the retrieved context to answer. {extra_instructions}"""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


def evaluator(ticket: str, context: list[str], draft: str) -> EvaluationResponse:
    prompt = f"""You are a strict QA reviewer for customer support replies.

Ticket:
{ticket}

Retrieved context (the ONLY source of truth):
{format_context(context)}

Generated response:
{draft}

Judge the response:
1. relevant: does it address the customer's issue?
2. faithful: is EVERY factual claim (timeframes, amounts, steps, policies) supported
   by the retrieved context? Any claim not in the context makes this false, even if plausible.
3. complete: does it adequately address the issue?
4. confidence: 0-1, how confident you are in this verdict.
5. feedback: what should be fixed; quote unsupported claims."""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EvaluationResponse,
            temperature=0,
        ),
    )
    return response.parsed


def run_pipeline(ticket: str, extra_instructions: str = ""):
    context = SupportRAG().retrieve(ticket)
    draft = generator(ticket, context, extra_instructions)
    return draft, evaluator(ticket, context, draft)


def show(title: str, draft: str, evaluation: EvaluationResponse):
    print(f"\n=== {title} ===")
    print(f"Draft:\n{draft}\n")
    print(evaluation.model_dump_json(indent=2))


if __name__ == "__main__":
    ticket = "Hi, I bought something last week and want a refund. How does that work?"

    # 1. Normal run: generator sticks to the context
    show("Normal draft", *run_pipeline(ticket))

    # 2. Bad generator: pushed to add an unsupported claim
    show(
        "Generator told to add an unsupported claim",
        *run_pipeline(
            ticket,
            "Also state that refunds are processed within 3 business days.",
        ),
    )

    # 3. Hand-written bad draft, bypassing the generator entirely
    context = SupportRAG().retrieve(ticket)
    bad_draft = (
        "You can request a refund within 30 days. "
        "Refunds are processed within 3 business days."
    )
    show("Hardcoded bad draft", bad_draft, evaluator(ticket, context, bad_draft))
