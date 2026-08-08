from pathlib import Path

from config import get_max_file_read_bytes
from tools.path_utils import resolve_path, tool_result


def read_file(path: str, max_bytes: int | None = None) -> str:
    """Read the contents of a text file."""

    try:
        file_path = resolve_path(path)
        limit = max_bytes or get_max_file_read_bytes()

        if not file_path.exists():
            return tool_result(False, error="File does not exist.")

        if not file_path.is_file():
            return tool_result(False, error="Path is not a file.")

        size = file_path.stat().st_size
        if size > limit:
            return tool_result(
                False,
                error=f"File too large ({size} bytes). Max allowed: {limit} bytes.",
            )

        content = file_path.read_text(encoding="utf-8", errors="replace")
        return tool_result(
            True,
            path=str(file_path),
            size_bytes=size,
            content=content,
        )

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
