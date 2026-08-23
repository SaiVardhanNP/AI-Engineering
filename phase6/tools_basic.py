from pydantic import BaseModel
from typing import Literal
import json
from tools_registry import tool_registry
from tool_dispatcher import tool_dispatcher
from tool_dispatcher import ToolCall


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
