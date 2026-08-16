import asyncio
import time

async def task(name):
    print(f"{name} started")
    await asyncio.sleep(2)
    print(f"{name} finished")

async def main():
    start = time.perf_counter()

    # First:
    # await task("A")
    # await task("B")

    # Then replace with:
    await asyncio.gather(
        task("A"),
        task("B")
    )

    end = time.perf_counter()

    print(f"Time: {end - start:.2f} seconds")

asyncio.run(main())



async def create(task:str):
    print(task," Started creating")
    await asyncio.sleep(2)
    print(task," Done with the creation")


async def run():
    await create("TaskA")

asyncio.run(run())
    