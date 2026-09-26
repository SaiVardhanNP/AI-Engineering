from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from dotenv import load_dotenv
import httpx
from pydantic import BaseModel
import os
import asyncio

load_dotenv()


class WeatherResult(BaseModel):
    city: str
    temperature: float


class WeatherInput(BaseModel):
    city: str


model = ChatGoogleGenerativeAI(
    api_key=os.getenv("GEMINI_API_KEY"), model="gemini-3.5-flash-lite"
)


@tool
def add_numbers(a: int, b: int) -> int:
    """Performs addition of two numbers"""
    return a + b


@tool
async def get_temperature(input: WeatherInput) -> WeatherResult:
    """Given the name of a city it will get the temperature of that particular city"""
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


agent = create_agent(model=model, tools=[add_numbers, get_temperature])


async def main():
    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What is the temperature at Hyderabad now and what is the sum of 30 + 50?",
                }
            ]
        }
    )
    print(result)


asyncio.run(main())
