import asyncio
import inspect

from google import genai
from google.genai import types

from config import GEMINI_API_KEY
from tools_registry import tool_registry
from models.model_output import AgentResponse


# ============================================================
# Tool Schemas
# ============================================================

temperature_tool = {
    "name": "get_temperature",
    "description": "Given a city name, return its current temperature.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city whose temperature should be retrieved.",
            }
        },
        "required": ["city"],
    },
}


calculator_tool = {
    "name": "calculator",
    "description": "Perform arithmetic operations on two numbers.",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {
                "type": "number",
                "description": "The first number.",
            },
            "b": {
                "type": "number",
                "description": "The second number.",
            },
            "operation": {
                "type": "string",
                "description": "The arithmetic operation to perform.",
                "enum": [
                    "addition",
                    "subtraction",
                    "multiplication",
                    "division",
                ],
            },
        },
        "required": ["a", "b", "operation"],
    },
}


# ============================================================
# Gemini Client
# ============================================================

client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# Tool Configuration
# ============================================================

tools_declaration = types.Tool(
    function_declarations=[
        temperature_tool,
        calculator_tool,
    ]
)


# Configuration used while the agent is deciding/executing tools
loop_config = types.GenerateContentConfig(
    tools=[tools_declaration]
)


# Configuration used for the final structured response
structured_final_config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=AgentResponse,
)


# ============================================================
# Tool Execution
# ============================================================

async def execute_tool_call(call):
    """
    Resolve, validate, execute, and validate the output
    of a single tool call.
    """

    # 1. Find tool metadata from registry
    tool = tool_registry[call.name]

    # 2. Validate Gemini's arguments
    validated_input = tool["input_model"](**call.args)

    # 3. Execute the actual tool
    result = tool["function"](validated_input)

    # 4. Support both sync and async tools
    if inspect.isawaitable(result):
        result = await result

    # 5. Validate the tool output
    validated_output = tool["output_model"].model_validate(result)

    return validated_output


# ============================================================
# Agent
# ============================================================

async def main():

    prompt = "What's the temperature in Hyderabad, and what is 125 * 48?"

    # Maximum number of tool-execution rounds allowed
    MAX_ITERATIONS = 5

    # --------------------------------------------------------
    # 1. Create Gemini chat session
    # --------------------------------------------------------

    chat = client.chats.create(
        model="gemini-3.5-flash-lite",
        config=loop_config,
    )

    print(
        f"🤖 Starting agent for prompt:\n"
        f"   {prompt}\n"
    )

    # --------------------------------------------------------
    # 2. Initial model request
    # --------------------------------------------------------

    response = chat.send_message(prompt)

    # --------------------------------------------------------
    # 3. Agentic tool loop
    # --------------------------------------------------------

    for iteration in range(MAX_ITERATIONS):

        print(
            f"🔄 Agent iteration {iteration + 1}/{MAX_ITERATIONS}"
        )

        # ----------------------------------------------------
        # No more tools → agent has finished gathering data
        # ----------------------------------------------------

        if not response.function_calls:

            print(
                "🎯 Gemini requested no more tools."
            )

            break

        print(
            f"🔧 Gemini requested "
            f"{len(response.function_calls)} tool call(s)"
        )

        # ----------------------------------------------------
        # Execute all requested tools concurrently
        # ----------------------------------------------------

        results = await asyncio.gather(
            *(
                execute_tool_call(call)
                for call in response.function_calls
            )
        )

        # ----------------------------------------------------
        # Convert tool results into Gemini function responses
        # ----------------------------------------------------

        function_responses = [
            types.Part.from_function_response(
                name=call.name,
                response=result.model_dump(),
            )
            for call, result in zip(
                response.function_calls,
                results,
            )
        ]

        # ----------------------------------------------------
        # Send tool results back to Gemini
        # ----------------------------------------------------

        response = chat.send_message(
            function_responses
        )

        print(
            "✅ Tool results sent back to Gemini.\n"
        )

    # --------------------------------------------------------
    # 4. Iteration budget exceeded
    # --------------------------------------------------------

    else:
        raise RuntimeError(
            f"Agent exceeded the maximum "
            f"of {MAX_ITERATIONS} iterations."
        )

    # --------------------------------------------------------
    # 5. Request final structured response
    # --------------------------------------------------------

    print(
        "🚀 Requesting structured final response..."
    )

    final_response = chat.send_message(
        "Format the gathered answers according to "
        "the requested response schema.",
        config=structured_final_config,
    )

    # --------------------------------------------------------
    # 6. Validate final Gemini output with Pydantic
    # --------------------------------------------------------

    agent_response = AgentResponse.model_validate_json(
        final_response.text
    )

    # --------------------------------------------------------
    # 7. Final result
    # --------------------------------------------------------

    print(
        "\n🚀 --- FINAL STRUCTURED AGENT OUTPUT ---"
    )

    print(agent_response)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())