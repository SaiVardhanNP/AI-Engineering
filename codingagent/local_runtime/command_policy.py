class CommandPolicy:
    ALLOWED_COMMANDS = {"pytest", "python", "pip"}

    def validate(self, command: str):
        command_name = command.strip().split()[0]

        if command_name not in self.ALLOWED_COMMANDS:
            raise ValueError(f"Command not allowed: {command_name}")
