from models.code_modification import CodeModificationInput


class CodeModificationPrompt:
    def build(self, data: CodeModificationInput) -> str:
        return f"""
You are a senior software engineer.

Modify the provided code according to the user's instruction.

Requirements:
- Follow the instruction exactly.
- Preserve existing functionality unless the instruction requires changes.
- Do not introduce unnecessary modifications.
- Keep the code clean, readable, and idiomatic.
- Maintain the original programming language and coding style.
- Ensure the modified code is syntactically correct.
- Return only the updated code.
- Do not include explanations or markdown code fences.

Instruction:
{data.instruction}

Code:
{data.code}
"""