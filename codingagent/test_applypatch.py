from agent.workspace import Workspace
from agent.tools.filesystem import create_filesystem_tools


workspace = Workspace("workspace/sample-project")

tools = create_filesystem_tools(workspace)

tool_map = {tool.name: tool for tool in tools}

result = tool_map["apply_patch"].invoke(
    {
        "path": "calculator.py",
        "old_text": 'elif operation == "mod":\n        return a % b',
        "new_text": 'elif operation == "mod":\n        return a % b\n    # modulus operation',
    }
)

print(result)
