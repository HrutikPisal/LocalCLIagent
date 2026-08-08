import io
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout

from config import get_command_timeout, get_max_python_output_chars
from tools.path_utils import resolve_path, tool_result


def run_python(code: str, directory: str = ".") -> str:
    """Execute a short Python snippet and return stdout/stderr."""

    if not code.strip():
        return tool_result(False, error="Code must not be empty.")

    blocked = ["import os", "import subprocess", "import shutil", "__import__", "open("]
    lowered = code.lower()
    for token in blocked:
        if token.lower() in lowered:
            return tool_result(
                False,
                error=f"Blocked construct in Python runner: {token}",
            )

    cwd = resolve_path(directory)
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    try:
        globals_dict = {"__name__": "__main__"}
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            exec(code, globals_dict, {})

        stdout = stdout_buffer.getvalue()
        stderr = stderr_buffer.getvalue()
        max_chars = get_max_python_output_chars()

        if len(stdout) > max_chars:
            stdout = stdout[:max_chars] + "\n... (truncated)"

        return tool_result(
            True,
            directory=str(cwd),
            stdout=stdout,
            stderr=stderr,
        )

    except Exception as exc:
        return tool_result(False, error=str(exc), stderr=stderr_buffer.getvalue())


def run_script(script_path: str, directory: str = ".") -> str:
    """Run a Python script file and capture output."""

    try:
        path = resolve_path(script_path)
        if not path.exists() or not path.is_file():
            return tool_result(False, error="Script file does not exist.")

        if path.suffix.lower() != ".py":
            return tool_result(False, error="Only .py scripts are supported.")

        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(resolve_path(directory)),
            capture_output=True,
            text=True,
            timeout=get_command_timeout(),
        )

        max_chars = get_max_python_output_chars()
        stdout = result.stdout
        if len(stdout) > max_chars:
            stdout = stdout[:max_chars] + "\n... (truncated)"

        return tool_result(
            success=result.returncode == 0,
            script=str(path),
            return_code=result.returncode,
            stdout=stdout,
            stderr=result.stderr,
        )

    except subprocess.TimeoutExpired:
        return tool_result(False, error="Script execution timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
