from pipelines.ai_pipeline import AIPipeline
from providers.grok import GroqProvider


def get_pipeline():
    return AIPipeline(GroqProvider())
