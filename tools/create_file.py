from pathlib import Path

from tools.path_utils import resolve_path, tool_result


def create_file(path: str, content: str = "") -> str:
    """Create a new file with optional content."""

    try:
        file_path = resolve_path(path)

        if file_path.exists():
            return tool_result(False, error="File already exists.")

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

        return tool_result(
            True,
            path=str(file_path),
            size_bytes=file_path.stat().st_size,
            message="File created.",
        )

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
