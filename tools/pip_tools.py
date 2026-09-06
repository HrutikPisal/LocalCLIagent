import json
import subprocess
import sys

from config import get_command_timeout
from tools.path_utils import resolve_path, tool_result

# Cap on how many packages are ever returned in one call. An uncapped environment
# listing can run to 150+ packages / ~9KB of JSON (observed in logs/agent_06_09_2026.txt),
# which then sits verbatim in conversation history for every later turn — on a model
# whose effective context window is a few thousand tokens, that alone can crowd out the
# system prompt and bias/confuse responses to later, unrelated messages. Keep this in
# sync with the same rationale in tools/read_directory.py and tools/search_files.py.
MAX_PACKAGES_LISTED = 50


def pip_list() -> str:
    """List installed Python packages."""

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=get_command_timeout(),
        )
        if result.returncode != 0:
            return tool_result(False, error=result.stderr.strip() or "pip list failed.")

        packages = json.loads(result.stdout.strip() or "[]")
        total_count = len(packages)
        truncated = total_count > MAX_PACKAGES_LISTED
        payload = {
            "packages": packages[:MAX_PACKAGES_LISTED],
            "count": min(total_count, MAX_PACKAGES_LISTED),
            "total_count": total_count,
        }
        if truncated:
            payload["truncated"] = True
            payload["note"] = (
                f"Showing first {MAX_PACKAGES_LISTED} of {total_count} packages. "
                "Ask about a specific package name for more detail."
            )
        return tool_result(True, **payload)
    except subprocess.TimeoutExpired:
        return tool_result(False, error="pip list timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def pip_install(package: str, directory: str = ".") -> str:
    """Install a Python package with pip."""

    if not package.strip():
        return tool_result(False, error="Package name must not be empty.")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package.strip()],
            cwd=str(resolve_path(directory)),
            capture_output=True,
            text=True,
            timeout=get_command_timeout() * 2,
        )
        return tool_result(
            success=result.returncode == 0,
            package=package.strip(),
            stdout=result.stdout.strip(),
            stderr=result.stderr.strip(),
        )
    except subprocess.TimeoutExpired:
        return tool_result(False, error="pip install timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
