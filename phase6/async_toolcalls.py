import asyncio
import httpx
from pydantic import BaseModel


class WeatherResult(BaseModel):
    city: str
    temperature: float


async def get_temperature(city: str) -> WeatherResult:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        )
        
        response= response.json()

        temperature = await client.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={response['results'][0]['latitude']}&longitude={response['results'][0]['longitude']}&current=temperature_2m"
        )
        
        temperature=temperature.json()

        return WeatherResult(
            city=city, temperature=temperature["current"]["temperature_2m"]
        )


async def main():
    results = await asyncio.gather(
        get_temperature("Hyderabad"), get_temperature("Bangalore")
    )

    for result in results:
        print(result)


asyncio.run(main())
