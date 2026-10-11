import asyncio

from langchain_core.messages import HumanMessage
from agent.graph import app


async def main():

    result = await app.ainvoke(
        {
            "messages": [HumanMessage(content="Run the tests for this project.")],
            "task_status": "working",
            "test_attempts": 0,
        },
        config={"recursion_limit": 35},
    )

    print("\nFINAL STATE:")
    print(result["task_status"])
    print(result["test_attempts"])

asyncio.run(main())
