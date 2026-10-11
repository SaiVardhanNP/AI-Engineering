from agent.workspace import Workspace
from agent.tools.filesystem import create_filesystem_tools
from agent.tools.search import create_search_tools
from agent.tools.shell import create_shell_tools
from local_runtime.protocol import ToolRequest, ToolResult


class LocalRuntime:
    def __init__(self, workspace_path: str):
        self.workspace = Workspace(workspace_path)

        file_system_tools = create_filesystem_tools(self.workspace)
        search_tools = create_search_tools(self.workspace)
        shell_tools = create_shell_tools(self.workspace)

        self.tools = file_system_tools + search_tools + shell_tools

        self.tool_registry = {tool.name: tool for tool in self.tools}

    def execute(self, request: ToolRequest) -> ToolResult:
        if request.tool_name not in self.tool_registry:
            return ToolResult(
                call_id=request.call_id,
                success=False,
                error=f"Unknown tool: {request.tool_name}",
            )
        try:
            tool = self.tool_registry[request.tool_name]

            result = tool.invoke(request.arguments)

            return ToolResult(
                call_id=request.call_id,
                success=True,
                content=result,
            )

        except Exception as e:
            return ToolRequest(call_id=request.call_id, success=False, error=str(e))
