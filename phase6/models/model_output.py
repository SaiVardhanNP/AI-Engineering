from pydantic import BaseModel


class WeatherSummary(BaseModel):
    city: str
    temperature: float


class CalculationSummary(BaseModel):
    expression: str
    result: float


class AgentResponse(BaseModel):
    weather: WeatherSummary
    calculation: CalculationSummary
