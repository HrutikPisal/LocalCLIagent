import subprocess
import sys

from config import get_command_timeout
from tools.path_utils import resolve_path, tool_result


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
        return tool_result(True, packages=result.stdout.strip())
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
