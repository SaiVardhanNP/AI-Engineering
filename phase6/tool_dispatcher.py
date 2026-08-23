from tools_registry import tool_registry
from pydantic import BaseModel
from tools.calculator_tool import CalculatorInput


class ToolCall(BaseModel):
    name: str
    arguments: CalculatorInput


def tool_dispatcher(input: ToolCall) -> dict:
    tool_name = input.name

    tool_function = tool_registry.get(tool_name)

    args = input.arguments

    result = tool_function(args)

    return {"name": tool_name, "result": result}
