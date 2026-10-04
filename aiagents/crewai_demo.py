import os

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

load_dotenv()


@tool("Get Order Status")
def get_order_status(order_id: str) -> str:
    """Get the current status of a customer order"""

    orders = {"ORD-101": "shipped", "ORD-102": "delivered", "ORD-103": "processing"}

    status = orders.get(order_id)

    if status is None:
        return f"Order {order_id} is not found."

    return f"Order {order_id} is currently {status}"


@tool("Search Support Docs")
def search_support_docs(query: str) -> str:
    """Search the customer support knowledge base for relevant information."""
    knowledge = {
        "refund": "Customers can request a refund within 30 days.",
        "password": "Customers can reset their password from Account Settings.",
        "shipping": "Standard shipping takes 5-7 business days.",
    }

    supported_docs = []

    for key, value in knowledge.items():
        if key in query.lower():
            supported_docs.append(value)

    if not supported_docs:
        return "No relevant support documentation found."

    return "\n".join(supported_docs)


# CrewAI routes through LiteLLM, so the "groq/" prefix selects the provider.
llm = LLM(
    model="openai/openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

billing_agent = Agent(
    llm=llm,
    role="Billing Specialist",
    goal="Investigate customer billing issues and provide accurate findings",
    backstory="""
    You are an experienced billing specialist.
    You investigate duplicate charges and subscription billing problems.
    You only provide internal findings.
    """,
)

support_agent = Agent(
    llm=llm,
    role="Customer Support Coordinator",
    tools=[get_order_status,search_support_docs],
    goal="Turn specialist findings into a clear customer-facing response",
    backstory="""
    You are an experienced customer support coordinator.
    You synthesize specialist findings into accurate customer responses.
    You must not invent actions that were not actually performed.
    """,
)


billing_task = Task(
    description="""
    Investigate this customer issue:

    The customer says:
    "I was charged twice for my Pro subscription."

    Determine what should be investigated and what the appropriate
    resolution would be.
    """,
    expected_output="""
    A concise internal billing investigation containing:
    - likely causes
    - what should be checked
    - recommended resolution
    """,
    agent=billing_agent,
)

support_task = Task(
    description="""
    What is 59 + 41?

    Do not claim that a refund was issued unless the findings
    explicitly confirm that an actual refund operation occurred.
    """,
    expected_output="""
    A professional customer-facing support response.
    """,
    agent=support_agent,
)

crew = Crew(
    agents=[billing_agent, support_agent],
    tasks=[support_task],
    process=Process.sequential,
    verbose=True,
)

result = crew.kickoff()

print(result)
