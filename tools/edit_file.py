"""Edit file tools for modifying existing files."""

from pathlib import Path

from config import get_max_file_read_bytes
from tools.path_utils import resolve_path, tool_result


def edit_file(path: str, find: str, replace: str) -> str:
    """Find and replace text in a file."""
    if not find:
        return tool_result(False, error="Find text must not be empty.")

    try:
        file_path = resolve_path(path)

        if not file_path.exists():
            return tool_result(False, error="File does not exist.")

        if not file_path.is_file():
            return tool_result(False, error="Path is not a file.")

        content = file_path.read_text(encoding="utf-8", errors="replace")

        if find not in content:
            return tool_result(
                False,
                error="Find text not found in file.",
                find=find,
            )

        new_content = content.replace(find, replace)
        file_path.write_text(new_content, encoding="utf-8")

        return tool_result(
            True,
            path=str(file_path),
            replacements=content.count(find),
            message="File edited successfully.",
        )

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def insert_line(path: str, line_number: int, content: str) -> str:
    """Insert a line at a specific line number."""
    if line_number < 1:
        return tool_result(False, error="Line number must be >= 1.")

    try:
        file_path = resolve_path(path)

        if not file_path.exists():
            return tool_result(False, error="File does not exist.")

        if not file_path.is_file():
            return tool_result(False, error="Path is not a file.")

        lines = file_path.read_text(encoding="utf-8", errors="replace").split("\n")

        if line_number > len(lines) + 1:
            return tool_result(
                False,
                error=f"Line number {line_number} exceeds file length ({len(lines)} lines).",
            )

        lines.insert(line_number - 1, content)
        file_path.write_text("\n".join(lines), encoding="utf-8")

        return tool_result(
            True,
            path=str(file_path),
            line_inserted=line_number,
            total_lines=len(lines),
            message="Line inserted successfully.",
        )

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def delete_line(path: str, line_number: int) -> str:
    """Delete a line at a specific line number."""
    if line_number < 1:
        return tool_result(False, error="Line number must be >= 1.")

    try:
        file_path = resolve_path(path)

        if not file_path.exists():
            return tool_result(False, error="File does not exist.")

        if not file_path.is_file():
            return tool_result(False, error="Path is not a file.")

        lines = file_path.read_text(encoding="utf-8", errors="replace").split("\n")

        if line_number > len(lines):
            return tool_result(
                False,
                error=f"Line number {line_number} exceeds file length ({len(lines)} lines).",
            )

        deleted_content = lines.pop(line_number - 1)
        file_path.write_text("\n".join(lines), encoding="utf-8")

        return tool_result(
            True,
            path=str(file_path),
            line_deleted=line_number,
            deleted_content=deleted_content,
            total_lines=len(lines),
            message="Line deleted successfully.",
        )

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
