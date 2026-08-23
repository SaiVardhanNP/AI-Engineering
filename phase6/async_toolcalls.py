import asyncio
import httpx
from pydantic import BaseModel
from tools.temperature_tool import get_temperature


async def main():
    results = await asyncio.gather(
        get_temperature("Hyderabad"), get_temperature("Bangalore")
    )

    for result in results:
        print(result)


asyncio.run(main())
