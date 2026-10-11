from langchain_core.messages import ToolMessage
from agent.remote_runtime import RemoteRuntimeClient
from local_runtime.protocol import ToolRequest


class RemoteToolNode:
    def __init__(self, runtime: RemoteRuntimeClient):
        self.runtime = runtime

    async def __call__(self, state):
        last_message = state["messages"][-1]

        tool_messages = []

        for tool_call in last_message.tool_calls:
            request = ToolRequest(
                call_id=tool_call["id"],
                tool_name=tool_call["name"],
                arguments=tool_call["args"],
            )

            result = await self.runtime.execute(request=request)

            if result.success:
                content = str(result.content)
            else:
                content = f"{tool_call['name']} execution failed: {result.error}"

            tool_messages.append(
                ToolMessage(
                    content=content,
                    tool_call_id=result.call_id,
                    name=tool_call["name"],
                )
            )
        return {"messages": tool_messages}
