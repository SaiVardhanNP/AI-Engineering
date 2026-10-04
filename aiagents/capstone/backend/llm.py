from crewai import LLM

from config import settings


def build_llm(provider):
    if provider == "gemini":
        return LLM(
            model="gemini/gemini-3.5-flash-lite",
            api_key=settings.gemini_api_key,
        )

    # Same Groq setup as aiagents/crewai_demo.py: Groq exposes an OpenAI-compatible
    # API, so the "openai/" prefix selects the provider and base_url points at Groq.
    return LLM(
        model="openai/openai/gpt-oss-120b",
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
    )


llm = build_llm(settings.agent_llm)
