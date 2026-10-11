from pathlib import Path


class Workspace:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

        if not self.root.exists():
            raise ValueError(f"Workspace does not exist: {self.root}")

        if not self.root.is_dir():
            raise ValueError(f"Workspace is not a directory: {self.root}")

    def resolve_path(self, path: str) -> Path:
        requested_path = (self.root / path).resolve()

        if not requested_path.is_relative_to(self.root):
            raise ValueError(f"Path is outside workspace: {path}")

        return requested_path
