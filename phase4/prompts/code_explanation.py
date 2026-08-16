from models.code_explanation import (
    CodeExplanationInput,
    CodeExplanationOutput,
)


class CodeExplanationPrompt:
    schema = CodeExplanationOutput.model_json_schema()

    def build(self, data: CodeExplanationInput) -> str:
        return f"""
You are a senior software engineer and programming mentor.

Analyze the provided code and explain what it does.

Requirements:
- Explain the overall purpose of the code.
- Describe how the main logic works.
- Highlight important functions, classes, or algorithms.
- Mention any notable implementation details if relevant.
- Return ONLY valid JSON that matches the following schema.
- Do not include markdown or code fences.

JSON Schema:
{self.schema}

Code:
{data.code}
"""
