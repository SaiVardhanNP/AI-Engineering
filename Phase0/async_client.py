import asyncio
import httpx
import time


async def get_user():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://jsonplaceholder.typicode.com/users/1")
            response.raise_for_status()
            data = response.json()
            print(data["name"])
        except Exception as e:
            print(e)


asyncio.run(get_user())


async def get_multiple_users():
    async with httpx.AsyncClient() as client:
        try:
            start = time.perf_counter()
            users = await asyncio.gather(
                client.get("https://jsonplaceholder.typicode.com/users/2"),
                client.get("https://jsonplaceholder.typicode.com/users/3"),
                client.get("https://jsonplaceholder.typicode.com/users/4"),
            )
            
            end= time.perf_counter()


            for user in users:
                print(user.json()["name"])
            print(f"Total time taken to fetch 3 users {end - start:.3f}")
        except Exception as e:
            print(e)


asyncio.run(get_multiple_users())
