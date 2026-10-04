import asyncio
import os

from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination

load_dotenv()


def get_order_status(order_id: str) -> str:
    """Get the current status of a customer order."""

    orders = {
        "ORD-101": "shipped",
        "ORD-102": "delivered",
        "ORD-103": "processing",
    }

    status = orders.get(order_id)

    if status is None:
        return f"Order {order_id} was not found."

    return f"Order {order_id} is currently {status}."


async def main():
    # Groq's OpenAI-compatible endpoint; model_info is required because
    # AutoGen doesn't recognise Groq model names.
    model_client = OpenAIChatCompletionClient(
        model="openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        model_info={
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,
            "family": "unknown",
        },
    )
    billing_agent = AssistantAgent(
        name="billing_agent",
        model_client=model_client,
        system_message="""
    You are a billing specialist.

    Investigate ONLY the duplicate-charge issue.
    Report concise internal findings (likely cause, what should be checked or
    refunded). Do NOT write to the customer and do NOT address the
    authentication/dashboard issue. Never say DONE.
    """,
    )
    support_agent = AssistantAgent(
        name="support_agent",
        model_client=model_client,
        system_message="""
    You are a customer support coordinator.

    Wait until BOTH billing_agent and technical_agent have posted their
    findings. Then synthesize them into a single customer-facing response
    that covers the duplicate charge and the authentication issue.

    End your final response with the word DONE.
    """,
    )

    technical_agent = AssistantAgent(
        name="technical_agent",
        model_client=model_client,
        system_message="""
    You are a technical support agent.

    Investigate ONLY the authentication/dashboard issue.
    Report concise internal findings (likely cause, troubleshooting steps).
    Do NOT write to the customer and do NOT address billing.
    Never say DONE.
    """,
    )

    # Only the support agent's final response can end the run; the cap is a
    # safety net against runaway conversations.
    termination = TextMentionTermination(
        "DONE", sources=["support_agent"]
    ) | MaxMessageTermination(12)

    selector_prompt = """Select the next speaker for a customer support workflow.

{roles}

Current conversation:
{history}

Rules:
- billing_agent and technical_agent each speak exactly once, giving findings only.
- support_agent speaks only after BOTH billing_agent and technical_agent have spoken.
- support_agent speaks last and produces the final customer-facing response.

Read the conversation, then select the next agent from {participants}. Return only the agent name."""

    team = SelectorGroupChat(
        participants=[billing_agent, technical_agent, support_agent],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=False,
    )

    result = await team.run(
        task="I was charged twice for my Pro subscription and now my dashboard is showing an authentication error."
    )

    for message in result.messages:
        print(message)
        print("\n---\n")

    await model_client.close()


asyncio.run(main())
