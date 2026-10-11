from local_runtime.runtime import LocalRuntime
from local_runtime.protocol import ToolRequest, ToolResult

runtime = LocalRuntime("workspace/sample-project")

request = ToolRequest(
    call_id="call_001", tool_name="read_file", arguments={"path": "calculator.py"}
)

result = runtime.execute(request=request)


print(result)
