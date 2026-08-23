import httpx
from pydantic import BaseModel


class WeatherResult(BaseModel):
    city: str
    temperature: float


class WeatherInput(BaseModel):
    city: str


async def get_temperature(input: WeatherInput) -> WeatherResult:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={input.city}&count=1&language=en&format=json"
        )

        response = response.json()

        temperature = await client.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={response['results'][0]['latitude']}&longitude={response['results'][0]['longitude']}&current=temperature_2m"
        )

        temperature = temperature.json()

        return WeatherResult(
            city=input.city, temperature=temperature["current"]["temperature_2m"]
        )
