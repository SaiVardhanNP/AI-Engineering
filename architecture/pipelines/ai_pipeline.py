from models.generate_request import GenerateRequest, ChatRequest
from providers.base import BaseProvider
from pydantic import BaseModel, ValidationError
from exceptions.pipeline import InvalidLLMResponseError
from fastapi import HTTPException
import time
from exceptions.provider import (
    ProviderRateLimitError,
    ProviderConnectionError,
    ProviderAuthenticationError,
)


MAX_RETRIES = 3
INITIAL_DELAY = 1


class AIPipeline:
    def __init__(self, provider: BaseProvider):
        self.provider = provider

    def _execute_with_retry(self, operation):
        for attempt in range(MAX_RETRIES):
            try:
                response = operation()
                return response
            except ProviderAuthenticationError:
                raise
            except (ProviderRateLimitError, ProviderConnectionError):
                if attempt != MAX_RETRIES - 1:
                    time.sleep(INITIAL_DELAY * (2**attempt))
                else:
                    raise

    def generate(
        self, request: GenerateRequest, response_model: type[BaseModel]
    ) -> str:
        response = self._execute_with_retry(lambda: self.provider.generate(request))

        try:
            parsed = response_model.model_validate_json(response)
        except ValidationError:
            raise InvalidLLMResponseError()
        return parsed

    def chat(self, request: ChatRequest) -> str:
        return self._execute_with_retry(lambda: self.provider.chat(request))
