from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()


class ClassificationResponse(BaseModel):
    categories: list[Literal["billing", "technical", "account"]] = Field(
        description="one or more categories the user query belongs to"
    )
    reason: str


model = ChatGoogleGenerativeAI(
    api_key=os.getenv("GEMINI_API_KEY"), model="gemini-3.5-flash-lite"
)


structured_model = model.with_structured_output(ClassificationResponse)


response = structured_model.invoke(
    "My card was charged for the premium plan but the app still shows me as on the free tier and none of the pro features are unlocking — can you fix this?"
)


print(response)
