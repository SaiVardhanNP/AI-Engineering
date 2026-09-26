from langchain_core.runnables import RunnableLambda
import asyncio


def uppercase(text: str) -> str:
    return text.upper()


def add_prefix(text: str) -> str:
    return f"RESULT: {text}"


chain = RunnableLambda(uppercase) | RunnableLambda(add_prefix)

# result = chain.batch(["Hello Langchain", "Hello Langgraph"])

# print(result)

# for chunk in chain.stream("Hello langchain"):
#     print(chunk)


async def main():
    result = await chain.ainvoke("Hello LangChain")
    print(result)


asyncio.run(main())
