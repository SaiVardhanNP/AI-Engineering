from agent.workspace import Workspace
from local_runtime.command_executor import CommandExecutor


workspace = Workspace("workspace/sample-project")

executor = CommandExecutor(workspace)

result = executor.execute('python -c "raise Exception(\'boom\')')

print(result)
print(type(result))
print(result.exit_code)
print(result.stdout)
