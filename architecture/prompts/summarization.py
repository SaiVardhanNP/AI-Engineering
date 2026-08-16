from models.summarization import SummarizationInput


class SummarizationPrompt:
    def build_prompt(self, data: SummarizationInput):
        return f"""
You are an expert summarizer.

Summarize the following text.

Summary length: {data.length}

Return your response in the following JSON format:

{{
  "title": "A short descriptive title",
  "bullets": [
    "Key point 1",
    "Key point 2",
    "Key point 3"
  ]
}}

Rules:
- Return only valid JSON.
- Do not include markdown or code fences.
- The JSON must contain exactly the keys "title" and "bullets".
- "title" should be a concise heading.
- "bullets" should contain the important points from the text.

Text:
{data.text}
"""
