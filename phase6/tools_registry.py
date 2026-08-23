from tools.temperature_tool import get_temperature, WeatherResult, WeatherInput
from tools.calculator_tool import calculator, CalculatorInput, CalculatorResult

tool_registry = {
    "calculator": {
        "function": calculator,
        "input_model": CalculatorInput,
        "output_model": CalculatorResult,
    },
    "get_temperature": {
        "function": get_temperature,
        "input_model": WeatherInput,
        "output_model": WeatherResult,
    },
}
