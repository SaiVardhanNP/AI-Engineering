import asyncio
import time


async def billing_workflow(ticket: str):
    print("Billing investigation started")
    await asyncio.sleep(3)

    print("Billing investigation completed")

    return {"agent": "billing", "finding": "duplicate charge detected"}


async def technical_workflow(ticket: str):
    print("Technical investigation started")
    await asyncio.sleep(4)

    print("technical investigation completed")

    return {"agent": "technical", "finding": "dashboard error detected"}


async def main():
    ticket = "I was charged twice and my dashboard is showing an error."

    start = time.perf_counter()

    billing_result, technical_result = await asyncio.gather(
        billing_workflow(ticket), technical_workflow(ticket)
    )

    elapsed = time.perf_counter() - start

    print(billing_result)
    print(technical_result)
    print(f"Total time: {elapsed:.2f}s")


asyncio.run(main())
