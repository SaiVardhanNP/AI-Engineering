from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage
import os
from dotenv import load_dotenv

load_dotenv()


@tool
def add_numbers(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


model = ChatGoogleGenerativeAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    model="gemini-3.5-flash-lite",
)


model_with_tools = model.bind_tools([add_numbers])


response = model_with_tools.invoke("What is the sum of 10 + 10?")


tool_call = response.tool_calls[0]

tool_result = add_numbers.invoke(tool_call["args"])

tool_message = ToolMessage(
    content=str(tool_result),
    tool_call_id=tool_call["id"],
)

messages = [
    ("human", "What is the sum of 10 + 10?"),
    response,
    tool_message,
]

final_response = model_with_tools.invoke(messages)

print(final_response.content)

