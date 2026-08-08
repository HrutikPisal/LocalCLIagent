import os
from pathlib import Path

from config import get_protected_path_names, get_workspace_root


def resolve_path(path_str: str) -> Path:
    """Resolve a user-supplied path to an absolute Path."""
    if not path_str or path_str.strip() in {".", ""}:
        return Path.cwd().resolve()
    expanded = os.path.expandvars(os.path.expanduser(path_str))
    return Path(expanded).resolve()


def get_workspace() -> Path:
    return get_workspace_root().resolve()


def _path_parts(path: Path) -> list[str]:
    return [part.lower() for part in path.parts]


def is_protected_path(path: Path) -> bool:
    """Return True if the path touches a protected Windows location."""
    parts = _path_parts(path.resolve())
    protected = [name.lower() for name in get_protected_path_names()]
    return any(part in protected for part in parts)


def is_inside_workspace(path: Path) -> bool:
    """Return True if path is inside the configured workspace root."""
    workspace = get_workspace()
    try:
        path.resolve().relative_to(workspace)
        return True
    except ValueError:
        return False


def tool_result(success: bool, **payload) -> str:
    import json

    body = {"success": success, **payload}
    return json.dumps(body, indent=2, ensure_ascii=False)
