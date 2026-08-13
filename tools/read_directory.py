from pathlib import Path
from datetime import datetime
import json

# Restrict browsing to this workspace.
# Set to None to allow all paths.
WORKSPACE = None

# Cap on how many directory entries are ever returned in one call. Uncapped listings
# on a large folder can produce several KB of JSON, which eats a large fraction of the
# qwen2.5:3b model's 4096-token context window in one tool result and has been observed
# causing the model's final response to be truncated mid-sentence when the remaining
# context runs out. Keep this in sync with the same rationale in tools/search_files.py.
MAX_DIRECTORY_ITEMS = 50


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

        entries = sorted(path.iterdir())
        total_count = len(entries)
        truncated = total_count > MAX_DIRECTORY_ITEMS

        items = []
        for item in entries[:MAX_DIRECTORY_ITEMS]:

            stat = item.stat()

            items.append({
                "name": item.name,
                "type": "Directory" if item.is_dir() else "File",
                "size_bytes": stat.st_size if item.is_file() else None,
                "modified": datetime.fromtimestamp(
                    stat.st_mtime
                ).strftime("%Y-%m-%d %H:%M:%S")
            })

        result = {
            "success": True,
            "directory": str(path),
            "count": len(items),
            "total_count": total_count,
            "items": items
        }
        if truncated:
            result["truncated"] = True
            result["note"] = (
                f"Showing first {MAX_DIRECTORY_ITEMS} of {total_count} entries. "
                "Ask about a specific subfolder for more detail."
            )

        return json.dumps(result, indent=2)

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
    