from client import gemini_client

from prompts.summarization import SummarizationPrompt
from prompts.tone_control import ToneControlPrompt
from prompts.translation import TranslationPrompt
from prompts.writing import WritingPrompt
from prompts.ticket_classification import TicketClassificationPrompt
from prompts.code_generation import CodeGenerationPrompt
from prompts.code_modification import CodeModificationPrompt
from prompts.code_explanation import CodeExplanationPrompt

from pydantic import ValidationError
from models.summarization import SummarizationInput, SummaryOutput
from models.tone_control import ToneInput
from models.translation import TranslationInput
from models.writing_improvement import ImproveWritingInput
from models.ticket import TicketInput, TicketClassification
from models.code_generation import CodeGenerationInput
from models.code_modification import CodeModificationInput
from models.code_explanation import (
    CodeExplanationInput,
    CodeExplanationOutput,
)


def ai_response(prompt: str) -> str:
    response = gemini_client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )
    return response.text


print("""
Choose feature

1. Summary
2. Translation
3. Rewrite Tone
4. Improve Writing
5. Ticket Classification
6. Generate Code
7. Modify Code
8. Explain Code
9. Exit
""")

while True:
    user_input = int(input("Enter choice: "))

    match user_input:
        case 1:
            text = input("Paste text: ")
            length = input("Select length (short/medium/long): ")

            data = SummarizationInput(text=text, length=length)
            prompt = SummarizationPrompt().build_prompt(data)

            response = ai_response(prompt)
            try:
                response = SummaryOutput.model_validate_json(response)
                print("\nSummary:\n")

                print(response.bullets)
            except ValidationError as e:
                print(e)

        case 2:
            text = input("Paste text: ")
            language = input("Target language: ")

            data = TranslationInput(
                text=text,
                target_language=language,
            )
            prompt = TranslationPrompt().build_prompt(data)

            response = ai_response(prompt)
            print("\nTranslation:\n")
            print(response)

        case 3:
            text = input("Paste text: ")
            tone = input("Tone (professional/friendly/casual/formal): ")

            data = ToneInput(
                text=text,
                tone=tone,
            )
            prompt = ToneControlPrompt().build_prompt(data)

            response = ai_response(prompt)
            print("\nRewritten Text:\n")
            print(response)

        case 4:
            text = input("Paste text: ")

            data = ImproveWritingInput(text=text)
            prompt = WritingPrompt().build_prompt(data)

            response = ai_response(prompt)
            print("\nImproved Writing:\n")
            print(response)
        case 5:
            text = input("Enter your query: ")
            data = TicketInput(ticket=text)

            prompt = TicketClassificationPrompt().build(data)

            response = ai_response(prompt)

            try:
                response = TicketClassification.model_validate_json(response)
                print(response)

                if response.priority == "high":
                    print("High Priority")
                if response.department == "billing":
                    print("Route to billing team")
            except ValidationError as e:
                print(e)

        case 6:
            language = input("Programming language: ")
            task = input("Describe the task: ")

            data = CodeGenerationInput(
                language=language,
                task=task,
            )

            prompt = CodeGenerationPrompt().build(data)

            response = ai_response(prompt)

            print("\nGenerated Code:\n")
            print(response)

        case 7:
            instruction = input("Modification instruction: ")

            print("Paste code (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)

            code = "\n".join(lines)

            data = CodeModificationInput(
                code=code,
                instruction=instruction,
            )

            prompt = CodeModificationPrompt().build(data)

            response = ai_response(prompt)

            print("\nModified Code:\n")
            print(response)

        case 8:
            print("Paste code (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)

            code = "\n".join(lines)

            data = CodeExplanationInput(code=code)

            prompt = CodeExplanationPrompt().build(data)

            response = ai_response(prompt)

            try:
                response = CodeExplanationOutput.model_validate_json(response)

                print("\nExplanation:\n")
                print(response)

            except ValidationError as e:
                print(e)

        case 9:
            print("Goodbye!")
            break
