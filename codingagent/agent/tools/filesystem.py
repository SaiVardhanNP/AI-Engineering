from langchain_core.tools import tool

from agent.workspace import Workspace


def create_filesystem_tools(workspace: Workspace):

    @tool
    def list_files() -> list[str]:
        """List all files inside the current workspace."""

        files = []

        for path in workspace.root.rglob("*"):
            if path.is_file():
                files.append(str(path.relative_to(workspace.root)))

        return files

    @tool
    def read_file(path: str) -> str:
        """Read the contents of a file inside the current workspace."""

        file_path = workspace.resolve_path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not file_path.is_file():
            raise ValueError(f"Not a file: {path}")

        return file_path.read_text(encoding="utf-8")

    @tool
    def write_file(path: str, content: str) -> str:
        """Write content to a file inside the current workspace."""
        file_path = workspace.resolve_path(path)

        if file_path.exists() and not file_path.is_file():
            raise ValueError(f"Not a file: {path}")

        file_path.write_text(content, encoding="utf-8")

        return f"Wrote {len(content)} characters to {path}"

    @tool
    def apply_patch(path: str, old_text: str, new_text: str) -> str:
        """Edit an existing file by replacing old_text with new_text.
        old_text must match exactly one location in the file (include enough
        surrounding lines to make it unique). Read the file first."""

        file_path = workspace.resolve_path(path)

        if not file_path.exists():
            raise ValueError(f"File not found: {path}")

        if not file_path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        content = file_path.read_text(encoding="utf-8")

        occurences = content.count(old_text)

        if occurences == 0:
            raise ValueError(f"Could not find the specified text in {path}")

        if occurences > 1:
            raise ValueError(
                f"The specified text appears {occurences} times in {path}. Patch must match exactly one location"
            )

        updated_content = content.replace(old_text, new_text, 1)

        file_path.write_text(updated_content, encoding="utf-8")

        return f"Successfully patched {path}"

    return [list_files, read_file, write_file, apply_patch]
