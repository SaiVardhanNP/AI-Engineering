import httpx


async def fetch_user(user_id: int) -> dict:

    async with httpx.AsyncClient() as client:
            user = await client.get(
                f"https://jsonplaceholder.typicode.com/users/{user_id}"
            )

            user.raise_for_status()

            return user.json()

