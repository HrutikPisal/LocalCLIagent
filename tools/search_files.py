from pathlib import Path

from tools.path_utils import resolve_path, tool_result

# Same rationale as tools/read_directory.py's MAX_DIRECTORY_ITEMS: the previous cap of
# 200 matches could alone produce a tool result larger than the model's entire 4096-token
# context window, which has been observed causing truncated/empty final responses.
MAX_SEARCH_MATCHES = 50


def search_files(directory: str = ".", pattern: str = "*", recursive: bool = True) -> str:
    """Search for files matching a glob pattern."""

    try:
        root = resolve_path(directory)

        if not root.exists():
            return tool_result(False, error="Directory does not exist.")

        if not root.is_dir():
            return tool_result(False, error="Path is not a directory.")

        globber = root.rglob(pattern) if recursive else root.glob(pattern)
        matches = []
        truncated = False
        for match in sorted(globber, key=lambda p: str(p).lower()):
            if match.is_file():
                if len(matches) >= MAX_SEARCH_MATCHES:
                    truncated = True
                    break
                matches.append(
                    {
                        "path": str(match),
                        "name": match.name,
                        "size_bytes": match.stat().st_size,
                    }
                )

        extra = {}
        if truncated:
            extra["truncated"] = True
            extra["note"] = (
                f"Showing first {MAX_SEARCH_MATCHES} matches. Use a narrower pattern "
                "or directory for a complete list."
            )

        return tool_result(
            True,
            directory=str(root),
            pattern=pattern,
            recursive=recursive,
            count=len(matches),
            matches=matches,
            **extra,
        )

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
