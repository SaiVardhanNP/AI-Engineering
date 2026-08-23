# tools/calculator_tool.py
from pydantic import BaseModel
from typing import Literal


class CalculatorInput(BaseModel):
    a: float
    b: float
    operation: Literal["addition", "subtraction", "multiplication", "division"]


class CalculatorResult(BaseModel):
    result: float


def calculator(input: CalculatorInput) -> CalculatorResult:
    match input.operation:
        case "addition":
            return CalculatorResult(result=input.a + input.b)

        case "subtraction":
            return CalculatorResult(result=input.a - input.b)

        case "multiplication":
            return CalculatorResult(result=input.a * input.b)

        case "division":
            if input.b == 0:
                raise ZeroDivisionError("Denominator cannot be zero")

            return CalculatorResult(result=input.a / input.b)

        case _:
            raise ValueError(f"Unsupported operation: {input.operation}")
