from google import genai
from google.genai import types

from config import GEMINI_API_KEY
from models.generate_request import GenerateRequest, ChatRequest
from providers.base import BaseProvider


DEFAULT_MODEL = "gemini-3.5-flash-lite"


class GeminiProvider(BaseProvider):
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def generate(self, request: GenerateRequest) -> str:
        return self._generate(
            contents=request.prompt,
            system_instruction=request.system_prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

    def chat(self, request: ChatRequest) -> str:
        gemini_request = self._to_gemini(request)

        return self._generate(
            contents=gemini_request["messages"],
            system_instruction=gemini_request["system_prompt"],
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

    def _generate(
        self,
        contents,
        system_instruction: str | None,
        model: str | None,
        temperature: float,
        max_tokens: int | None,
    ) -> str:

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
        )

        if max_tokens is not None:
            config.max_output_tokens = max_tokens

        response = self.client.models.generate_content(
            model=model or DEFAULT_MODEL,
            contents=contents,
            config=config,
        )

        return response.text

    def _to_gemini(self, request: ChatRequest) -> dict:
        role_map = {
            "user": "user",
            "assistant": "model",
        }

        system_prompt = next(
            (
                message.content
                for message in request.messages
                if message.role == "system"
            ),
            None,
        )

        messages = [
            {
                "role": role_map[message.role],
                "parts": [
                    {
                        "text": message.content,
                    }
                ],
            }
            for message in request.messages
            if message.role != "system"
        ]

        return {
            "system_prompt": system_prompt,
            "messages": messages,
        }
