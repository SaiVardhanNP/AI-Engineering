from pydantic import BaseModel
from typing import Literal
import json


class CalculatorInput(BaseModel):
    a: float
    b: float
    operation: Literal["addition", "subtraction", "multiplication", "division"]


class ToolCall(BaseModel):
    name: str
    arguments: CalculatorInput


calculator_schema = {
    "name": "calculator",
    "type": "function",
    "description": "responsible for performing arithmetic operations.",
    "parameters": {
        "type": "object",
        "arguments": {
            "a": {"description": "first number in the operation", "type": "number"},
            "b": {"description": "second number in the operation", "type": "number"},
            "operation": {
                "description": "what arithemtic operation to be performed",
                "type": "string",
            },
        },
        "required": ["a", "b", "operation"],
    },
}


def calculator(input: CalculatorInput) -> float:
    match input.operation.strip():
        case "addition":
            return input.a + input.b
        case "subtraction":
            return input.a - input.b
        case "multiplication":
            return input.a * input.b
        case "division":
            if input.b == 0:
                raise ZeroDivisionError("Denominator cannot be zero")
            return input.a / input.b
        case _:
            raise ValueError("Invalid operation")


tool_registry = {"calculator": calculator}


def tool_dispatcher(input: ToolCall) -> dict:
    tool_name = input.name

    tool_function = tool_registry.get(tool_name)

    args = input.arguments

    result = tool_function(args)

    return {"name": tool_name, "result": result}


tool_calls = [
    {
        "name": "calculator",
        "arguments": {"a": 10, "b": 5, "operation": "multiplication"},
    },
    {"name": "calculator", "arguments": {"a": 20, "b": 4, "operation": "division"}},
]

tool_results = [
    tool_dispatcher(ToolCall(name=tool_call["name"], arguments=tool_call["arguments"]))
    for tool_call in tool_calls
]

for result in tool_results:
    print(result)
