from langchain_core.tools import tool

from agent.workspace import Workspace


def create_search_tools(workspace: Workspace):

    @tool
    def search_files(query: str) -> list[dict[str, str | int]]:
        """Search for text across files in the current workspace."""

        results = []

        for path in workspace.root.rglob("*"):
            if not path.is_file():
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue

            for line_number, line in enumerate(
                content.splitlines(),
                start=1,
            ):
                if query.lower() in line.lower():
                    results.append(
                        {
                            "file": str(path.relative_to(workspace.root)),
                            "line": line_number,
                            "content": line.strip(),
                        }
                    )

        return results

    return [search_files]
