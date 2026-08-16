from gemini_client import client
from google.genai import types
from history import add_assistant_message, add_user_message, trim_history, messages
from adapter import to_gemini
from pydantic_models import Ticket
from pydantic import ValidationError


def ai_response(messages: list, system_prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        config=types.GenerateContentConfig(system_instruction=system_prompt),
        contents=messages,
    )
    return response.text


print("Hey how can i help you? Type exit to get out of it.")


while True:
    try:
        user_input = input("You: ")
        if user_input.strip().lower() == "exit":
            print("Bot:See you soon again!")
            print(messages)
            break
        add_user_message(user_input)
        history_data = to_gemini(messages)
        response = ai_response(history_data["messages"], history_data["system_prompt"])
        try:
            validated_response = Ticket.model_validate_json(response)
        except ValidationError as e:
            print(e)
        add_assistant_message(response)
        trim_history(2)

        print("Bot: ", response)
    except Exception as e:
        print(e)
