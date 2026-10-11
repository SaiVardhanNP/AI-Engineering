from langchain_core.tools import tool

from agent.workspace import Workspace
from local_runtime.command_executor import CommandExecutor


def create_shell_tools(workspace: Workspace):
    executor = CommandExecutor(workspace)

    @tool
    def run_command(command: str) -> str:
        """Run a shell command inside the workspace and return its exit code,
        stdout and stderr. Only a limited set of commands is allowed (for
        example pytest and python). Use it to run tests or scripts."""

        try:
            result = executor.execute(command)
        except ValueError as error:
            return f"Command rejected: {error}"
        return (
            f"exit_code: {result.exit_code}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    return [run_command]
