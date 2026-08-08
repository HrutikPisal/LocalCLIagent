from pathlib import Path

from tools.path_utils import resolve_path, tool_result


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
        for match in sorted(globber, key=lambda p: str(p).lower()):
            if match.is_file():
                matches.append(
                    {
                        "path": str(match),
                        "name": match.name,
                        "size_bytes": match.stat().st_size,
                    }
                )
            if len(matches) >= 200:
                break

        return tool_result(
            True,
            directory=str(root),
            pattern=pattern,
            recursive=recursive,
            count=len(matches),
            matches=matches,
        )

    except PermissionError:
        return tool_result(False, error="Permission denied.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
