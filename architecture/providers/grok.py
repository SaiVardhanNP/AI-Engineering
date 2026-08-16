from groq import Groq, RateLimitError, AuthenticationError, APIConnectionError

from config import settings
from models.generate_request import GenerateRequest, ChatRequest
from providers.base import BaseProvider
from exceptions.provider import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderRateLimitError,
)


DEFAULT_MODEL = "llama-3.3-70b-versatile"


class GroqProvider(BaseProvider):
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)

    def generate(self, request: GenerateRequest) -> str:
        messages = []

        if request.system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": request.system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": request.prompt,
            }
        )

        return self._generate(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

    def chat(self, request: ChatRequest) -> str:
        messages = [message.model_dump() for message in request.messages]

        return self._generate(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

    def _generate(
        self,
        messages: list[dict],
        model: str | None,
        temperature: float,
        max_tokens: int | None,
    ) -> str:

        kwargs = {
            "model": model or DEFAULT_MODEL,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        try:
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except RateLimitError as e:
            raise ProviderRateLimitError() from e
        except AuthenticationError as e:
            raise ProviderAuthenticationError() from e
        except APIConnectionError as e:
            raise ProviderConnectionError() from e
