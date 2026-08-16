from abc import ABC, abstractmethod
from models.generate_request import GenerateRequest, ChatRequest


class BaseProvider(ABC):
    @abstractmethod
    def generate(self, request: GenerateRequest) -> str:
        """Generate a response from an LLM"""
        raise NotImplementedError

    @abstractmethod
    def chat(self, request: ChatRequest) -> str:
        """Generate a chat response from an LLM"""
