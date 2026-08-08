from pathlib import Path
from datetime import datetime
import json

# Restrict browsing to this workspace.
# Set to None to allow all paths.
WORKSPACE = None


def is_path_allowed(path: Path) -> bool:
    """
    Check whether the requested path is inside the workspace.
    """

    if WORKSPACE is None:
        return True

    try:
        path.resolve().relative_to(WORKSPACE)
        return True
    except ValueError:
        return False


def read_directory(directory: str = ".") -> str:
    """
    Lists all files and folders inside a directory.

    Returns a JSON string.
    """

    try:

        path = Path(directory).expanduser().resolve()

        if not path.exists():
            return json.dumps({
                "success": False,
                "error": "Directory does not exist."
            }, indent=2)

        if not path.is_dir():
            return json.dumps({
                "success": False,
                "error": "Path is not a directory."
            }, indent=2)

        if not is_path_allowed(path):
            return json.dumps({
                "success": False,
                "error": "Access denied by policy."
            }, indent=2)

        items = []

        for item in sorted(path.iterdir()):

            stat = item.stat()

            items.append({
                "name": item.name,
                "type": "Directory" if item.is_dir() else "File",
                "size_bytes": stat.st_size if item.is_file() else None,
                "modified": datetime.fromtimestamp(
                    stat.st_mtime
                ).strftime("%Y-%m-%d %H:%M:%S")
            })

        return json.dumps({
            "success": True,
            "directory": str(path),
            "count": len(items),
            "items": items
        }, indent=2)

    except PermissionError:

        return json.dumps({
            "success": False,
            "error": "Permission denied."
        }, indent=2)

    except Exception as e:

        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


if __name__ == "__main__":

    print(read_directory("."))
    