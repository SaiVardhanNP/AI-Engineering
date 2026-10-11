import subprocess
from local_runtime.command_policy import CommandPolicy
from pydantic import BaseModel


class CommandResult(BaseModel):
    command: str
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False


class CommandExecutor:
    def __init__(self, workspace: str):
        self.workspace = workspace
        self.policy = CommandPolicy()

    def execute(self, command: str) -> CommandResult:
        self.policy.validate(command)

        try:
            result = subprocess.run(
                command,
                cwd=self.workspace.root,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )

            return CommandResult(
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )

        except subprocess.TimeoutExpired as e:
            return CommandResult(
                command=command,
                exit_code=-1,
                stdout=e.stdout or "",
                stderr=e.stderr or "Command timed out.",
                timed_out=True,
            )
