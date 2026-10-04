from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()


def calculator(a: int, b: int, op: str) -> int:
    if op == "addition":
        return a + b
    elif op == "subtraction":
        return a - b
    elif op == "multiplication":
        return a * b
    elif op == "division":
        return a / b
    else:
        raise ValueError("Invalid operation")


def weather(city: str) -> str:
    return f"The temperature at {city} is very cool today."


calculator_decl = {
    "name": "calculator",
    "description": "given the inputs which includes the numbers a, and and operation it will be able to perform the arithemtic operation",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {
                "type": "integer",
                "description": "the first number of the operation",
            },
            "b": {
                "type": "integer",
                "description": "the second number of the operation",
            },
            "op": {
                "type": "string",
                "enum": ["addition", "subtraction", "multiplication", "division"],
                "description": "the operation that needs to be performed",
            },
        },
        "required": ["a", "b", "op"],
    },
}


weather_decl = {
    "name": "weather",
    "description": "given a name of city it will be able to give the temperature of that particular city",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "the name of the city for which we are trying to get the temperature",
            }
        },
        "required": ["city"],
    },
}


tools = types.Tool(function_declarations=[calculator_decl, weather_decl])
available_functions = {"calculator": calculator, "weather": weather}

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
config = types.GenerateContentConfig(tools=[tools])

MAX_STEPS = 10


def run_agent(prompt: str) -> str:
    contents = [types.Content(role="user", parts=[types.Part(text=prompt)])]

    for _ in range(MAX_STEPS):
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config=config,
        )

        # keep the model's turn (including its function calls) in the history
        contents.append(response.candidates[0].content)

        if not response.function_calls:
            return response.text

        # run every requested tool and send all results back in one turn
        result_parts = []
        for call in response.function_calls:
            print(f"-> {call.name}({dict(call.args)})")
            try:
                result = {"result": available_functions[call.name](**call.args)}
            except Exception as e:
                result = {"error": str(e)}
            result_parts.append(
                types.Part.from_function_response(name=call.name, response=result)
            )
        contents.append(types.Content(role="user", parts=result_parts))

    return "Stopped: reached MAX_STEPS without a final answer."


print(
    run_agent(
        "Hey what is the weather at Hyderabad Today and what is the sum of the 59+1?"
    )
)
