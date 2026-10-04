from smolagents import CodeAgent, LiteLLMModel, tool
from dotenv import load_dotenv
from smolagents import DuckDuckGoSearchTool
from rag_tool import SupportRAG
import os

load_dotenv()


orders = {
    "ORD-101": "shipped",
    "ORD-102": "delivered",
    "ORD-103": "processing",
}
rag = SupportRAG()
web_search_tool = DuckDuckGoSearchTool(max_results=5, rate_limit=2.0)


@tool
def calculator(a: int, b: int, op: str) -> float:
    """Perform an arithmetic operation on two numbers.

    Args:
        a: the first number of the operation
        b: the second number of the operation
        op: the operation to perform, one of "addition", "subtraction", "multiplication", "division"
    """
    if op == "addition":
        return a + b
    elif op == "subtraction":
        return a - b
    elif op == "multiplication":
        return a * b
    elif op == "division":
        return a / b
    else:
        raise ValueError("Invalid operation")


@tool
def weather(city: str) -> str:
    """Get the temperature of a city.

    Args:
        city: the name of the city for which we are trying to get the temperature
    """
    return f"The temperature at {city} is very cool today."


@tool
def get_order_status(order_id: str) -> str:
    """Get the current status of a customer order.

    Args:
        order_id: The order ID, for example ORD-101.
    """
    status = orders.get(order_id)

    if status is None:
        return f"Order {order_id} was not found."

    return f"Order {order_id} is currently {status}."


@tool
def search_support_docs(query: str) -> str:
    """Search the customer support knowledge base.

    Use this tool when answering questions about company
    policies, products, troubleshooting, shipping, refunds,
    or account procedures.

    Args:
        query: The specific information you need to find.
    """

    results = rag.retrieve(query)

    if not results:
        return "No relevant support documentation was found."

    return "\n".join(results)


model = LiteLLMModel(
    model_id="gemini/gemini-3.5-flash-lite",
    api_key=os.getenv("GEMINI_API_KEY"),
    num_retries=3,
)

# CodeAgent writes Python that calls our tools, instead of emitting JSON tool calls
agent = CodeAgent(
    tools=[calculator, weather, get_order_status, search_support_docs, web_search_tool],
    model=model,
    max_steps=10,
    instructions="Answer in a complete, friendly sentence.",
)

print(
    agent.run(
        "What are the latest developments in Python and what is the status of order 101"
    )
)
