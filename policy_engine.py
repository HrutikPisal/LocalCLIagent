from enum import Enum
from pathlib import Path

from config import get_dangerous_patterns
from tools.path_utils import is_inside_workspace, is_protected_path, resolve_path


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


PERMISSION_LEVELS = {
    "read": 1,
    "workspace_write": 2,
    "system_write": 3,
    "dangerous": 4,
}


PATH_ARGUMENT_KEYS = {
    "path",
    "directory",
    "source",
    "destination",
    "source_path",
    "destination_path",
    "file_path",
    "folder",
}


class PolicyEngine:
    """Evaluates tool calls before execution."""

    def evaluate(self, tool_name: str, arguments: dict, tool_entry: dict) -> tuple[PolicyDecision, str]:
        permission = tool_entry.get("permission", "read")
        level = PERMISSION_LEVELS.get(permission, 1)

        dangerous_reason = self._check_dangerous_content(tool_name, arguments)
        if dangerous_reason:
            return PolicyDecision.DENY, dangerous_reason

        path_reason = self._check_paths(arguments, permission)
        if path_reason:
            return PolicyDecision.DENY, path_reason

        if level <= 1:
            return PolicyDecision.ALLOW, "Read-only tool auto-approved."

        if level == 2:
            return PolicyDecision.REQUIRE_APPROVAL, "Workspace write requires owner approval."

        if level == 3:
            return PolicyDecision.REQUIRE_APPROVAL, "System write requires explicit approval."

        return PolicyDecision.REQUIRE_APPROVAL, "Dangerous operation requires explicit approval."

    def _check_dangerous_content(self, tool_name: str, arguments: dict) -> str | None:
        patterns = get_dangerous_patterns()
        haystack = f"{tool_name} {arguments}".lower()
        for pattern in patterns:
            if pattern.lower() in haystack:
                return f"Blocked dangerous pattern: {pattern}"
        return None

    def _check_paths(self, arguments: dict, permission: str) -> str | None:
        paths = self._extract_paths(arguments)
        if not paths:
            return None

        write_like = permission in {"workspace_write", "system_write", "dangerous"}

        for raw_path in paths:
            path = resolve_path(raw_path)

            if write_like and is_protected_path(path):
                return f"Write/delete blocked on protected path: {path}"

            if permission == "workspace_write" and not is_inside_workspace(path):
                return f"Write operations restricted to workspace: {get_workspace()}"

            if permission == "dangerous" and is_protected_path(path):
                return f"Dangerous operation blocked on protected path: {path}"

        return None

    def _extract_paths(self, arguments: dict) -> list[str]:
        paths: list[str] = []
        for key, value in arguments.items():
            if key in PATH_ARGUMENT_KEYS and isinstance(value, str):
                paths.append(value)
        return paths


def get_workspace() -> Path:
    from tools.path_utils import get_workspace as _get_workspace

    return _get_workspace()
