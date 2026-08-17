"""Terminal input/output reading tools."""

import subprocess
import sys

from config import get_command_timeout
from tools.path_utils import tool_result


def execute_command(command: str, cwd: str = ".") -> str:
    """Execute a shell command and capture output."""
    if not command.strip():
        return tool_result(False, error="Command must not be empty.")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=get_command_timeout(),
        )

        return tool_result(
            result.returncode == 0,
            command=command,
            return_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )

    except subprocess.TimeoutExpired:
        return tool_result(False, error="Command execution timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def run_command(command: str, cwd: str = ".", shell: bool = False) -> str:
    """Run a command as a list or shell string."""
    if not command.strip():
        return tool_result(False, error="Command must not be empty.")

    try:
        # Parse command if not shell mode
        if shell:
            cmd = command
        else:
            cmd = command.split()

        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=get_command_timeout(),
        )

        return tool_result(
            result.returncode == 0,
            command=command,
            return_code=result.returncode,
            stdout=result.stdout.strip(),
            stderr=result.stderr.strip(),
        )

    except subprocess.TimeoutExpired:
        return tool_result(False, error="Command execution timed out.")
    except FileNotFoundError:
        return tool_result(False, error="Command not found.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def get_output(command: str) -> str:
    """Execute command and return only stdout."""
    if not command.strip():
        return tool_result(False, error="Command must not be empty.")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=get_command_timeout(),
        )

        if result.returncode != 0:
            return tool_result(False, error=result.stderr.strip() or "Command failed.")

        return tool_result(
            True,
            command=command,
            output=result.stdout.strip(),
        )

    except subprocess.TimeoutExpired:
        return tool_result(False, error="Command execution timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
