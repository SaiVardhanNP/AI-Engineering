from langchain_core.tools import tool
from pydantic import BaseModel, Field, field_validator
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, ToolMessage
from db import get_connection
from llm import get_llm
from memory import preferences_as_text, remember_preference

USER = "sai"

conn = get_connection()


class Preference(BaseModel):
    preferred: str = Field(description="The option the user chose")
    over: str = Field(
        description="The option the user rejected in favour of `preferred`"
    )

    @field_validator("preferred", "over")
    @classmethod
    def normalise(cls, value: str) -> str:
        # "Express", " express " and "EXPRESS" must be the same node in the graph.
        return value.strip().lower()


# ---- Step A: tools ----------------------------------------------------------


@tool
def get_preferences() -> str:
    """Look up everything the user has said they prefer or reject."""
    return preferences_as_text(conn, USER)


@tool(args_schema=Preference)
def save_preference(preferred: str, over: str) -> str:
    """Save a preference when the user says they prefer one thing over another."""
    try:
        remember_preference(conn=conn, user=USER, preferred=preferred, over=over)
        return "The preference has been saved successfully!"
    except Exception as e:
        # Return, don't raise: the model sees the error as the tool result.
        return f"Failed to save preference: {e}"


# ---- Step B: prompt ---------------------------------------------------------
SYSTEM_PROMPT = """You are a helpful assistant that remembers the user's preferences between conversations.

Tools:
- save_preference: call it ONLY when the user clearly states that they prefer one specific thing over another, e.g. "I prefer Express over Fastify" or "React is better than Vue for me". Pass the chosen option as `preferred` and the rejected option as `over`.
- get_preferences: call it when the user asks what they prefer or like and the answer is not already in the known preferences below.

Do NOT call save_preference for questions, small talk, or a liking with no alternative (e.g. "I like pizza"). If it is unclear which option the user chose, ask a short clarifying question instead of guessing.

Only state preferences that appear in the known preferences or in a tool result. Never invent one. After saving a preference, confirm it to the user in one short sentence.

Known preferences: {preferences}"""

prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), MessagesPlaceholder("messages")]
)

# ---- Step C: agent loop -----------------------------------------------------

model = get_llm()

model_with_tools = model.bind_tools([save_preference, get_preferences])

tool_registry = {
    "save_preference": save_preference,
    "get_preferences": get_preferences,
}

chain = prompt | model_with_tools

messages = []

while True:
    user_message = input("You: ")

    if user_message.strip().lower() == "exit":
        break
    messages.append(HumanMessage(content=user_message))

    response = chain.invoke(
        {"preferences": preferences_as_text(conn=conn, user=USER), "messages": messages}
    )

    messages.append(response)

    while response.tool_calls:
        tool_messages = []
        for tool_call in response.tool_calls:
            tool_call_name = tool_call["name"]
            tool_call_id = tool_call["id"]
            tool_call_args = tool_call["args"]

            tool_fn = tool_registry.get(tool_call_name)
            if tool_fn is None:
                tool_result = f"Unknown tool: {tool_call_name}"
            else:
                tool_result = tool_fn.invoke(tool_call_args)

            tool_messages.append(
                ToolMessage(
                    content=tool_result,
                    name=tool_call_name,
                    tool_call_id=tool_call_id,
                )
            )
        messages.extend(tool_messages)

        response = chain.invoke(
            {
                "preferences": preferences_as_text(conn=conn, user=USER),
                "messages": messages,
            }
        )
        messages.append(response)

    print(f"AI: {response.text}")
