from pathlib import Path

from tools.path_utils import resolve_path, tool_result


def search_text(
    directory: str = ".",
    query: str = "",
    file_pattern: str = "*",
    max_matches: int = 50,
) -> str:
    """Search for text inside files within a directory."""

    if not query.strip():
        return tool_result(False, error="Query must not be empty.")

    try:
        root = resolve_path(directory)

        if not root.exists() or not root.is_dir():
            return tool_result(False, error="Directory does not exist.")

        matches = []
        truncated = False
        for file_path in root.rglob(file_pattern):
            if not file_path.is_file():
                continue
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
            except (PermissionError, OSError):
                continue

            for line_no, line in enumerate(text.splitlines(), start=1):
                if query.lower() in line.lower():
                    if len(matches) >= max_matches:
                        truncated = True
                        break
                    matches.append(
                        {
                            "path": str(file_path),
                            "line": line_no,
                            "text": line.strip()[:300],
                        }
                    )
            if truncated:
                break

        extra = {}
        if truncated:
            extra["truncated"] = True
            extra["note"] = (
                f"Showing first {max_matches} matches. Use a narrower query or "
                "file_pattern for a complete list."
            )

        return tool_result(
            True,
            directory=str(root),
            query=query,
            count=len(matches),
            matches=matches,
            **extra,
        )

    except Exception as exc:
        return tool_result(False, error=str(exc))
