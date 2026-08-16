import httpx
import asyncio

async def run():
    with httpx.AsyncClient() as client:
        response = await client.get("https://jsonplaceholder.typicode.com/todos/1")
        print(response.json())

asyncio.run(run())