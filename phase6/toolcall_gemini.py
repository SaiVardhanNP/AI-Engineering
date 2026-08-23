from google import genai
from config import GEMINI_API_KEY
from tools.temperature_tool import get_temperature
from google.genai import types
import asyncio
from tools_registry import tool_registry
import inspect

temperature_tool = {
    "name": "get_temperature",
    # "type": "function",
    "description": "given a city name it will be able to return its temperature",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city whose temperature to be retrieved",
            }
        },
        "required": ["city"],
    },
}

calculator_tool = {
    "name": "calculator",
    # "type": "function",
    "description": "responsible for performing arithmetic operations.",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {"description": "first number in the operation", "type": "number"},
            "b": {"description": "second number in the operation", "type": "number"},
            "operation": {
                "description": "The arithmetic operation to perform.",
                "type": "string",
                "enum": [
                    "addition",
                    "subtraction",
                    "multiplication",
                    "division",
                ],
            },
        },
        "required": ["a", "b", "operation"],
    },
}

client = genai.Client(api_key=GEMINI_API_KEY)

tools = types.Tool(function_declarations=[temperature_tool, calculator_tool])
config = types.GenerateContentConfig(tools=[tools])
forced_tool_config = types.GenerateContentConfig(
    tools=[tools],
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode="ANY",
            allowed_function_names=["get_temperature"],
        )
    ),
)


async def execute_tool_call(call):
    tool = tool_registry[call.name]
    validated_input = tool["input_model"](**call.args)

    result = tool["function"](validated_input)
    if inspect.isawaitable(result):
        result = await result
    validated_output= tool['output_model'].model_validate(result)
    return validated_output


async def main():
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="What's the temperature in Hyderabad, and what is 125 * 48?",
        config=config,
    )
    function_calls = response.function_calls
    # print(function_calls)
    results = await asyncio.gather(
        *(execute_tool_call(call) for call in function_calls)
    )

    function_responses = [
        types.Part.from_function_response(
            name=call.name,
            # Universal check: extracts dictionary from Pydantic model or wraps primitive floats/ints
            response=result.model_dump(),
        )
        for call, result in zip(function_calls, results)
    ]

    # for function_response in function_responses:
    #     print(function_response)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text="What's the temperature in Hyderabad, and what is 125 * 48??"
                )
            ],
        ),
        response.candidates[0].content,
        types.Content(role="user", parts=function_responses),
    ]

    final_response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=contents,
        config=config,
    )
    print(final_response.text)


asyncio.run(main())
