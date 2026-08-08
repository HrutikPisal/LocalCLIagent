from tools.path_utils import resolve_path, tool_result


def write_file(path: str, content: str) -> str:
    """Write content to an existing or new file."""

    try:
        file_path = resolve_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

        return tool_result(
            True,
            path=str(file_path),
            size_bytes=file_path.stat().st_size,
            message="File written.",
        )

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
