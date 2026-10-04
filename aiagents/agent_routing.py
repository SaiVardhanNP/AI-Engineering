from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
from typing import Literal
from pydantic import BaseModel, Field

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class ClassificationResponse(BaseModel):
    categories: list[Literal["billing", "technical", "account"]] = Field(
        description="one or more categories the user query belongs to"
    )
    reason: str = Field(
        description="Brief explanation of why these categories are selected"
    )


def classifer(query: str) -> ClassificationResponse:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=query,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ClassificationResponse,
        ),
    )
    return response.parsed


def route_request(classification: ClassificationResponse):
    routes = []

    if "billing" in classification.categories:
        routes.append("billing_workflow")
    if "technical" in classification.categories:
        routes.append("technical_workflow")
    if "account" in classification.categories:
        routes.append("account_workflow")
    return routes


result = classifer(
    "I was charged twice for my Pro subscription."
)

routes = route_request(result)

print(result)

print(routes)
