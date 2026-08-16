from api import fetch_user
from utils import format_user
import asyncio


user_id = int(input("Enter the userId: "))


async def main():
    user = await fetch_user(user_id)

    formatted_user = format_user(user)

    print(formatted_user)


asyncio.run(main())
