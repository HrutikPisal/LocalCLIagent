import subprocess

from config import get_command_timeout
from tools.path_utils import resolve_path, tool_result


def _run_git(args: list[str], directory: str) -> subprocess.CompletedProcess[str]:
    cwd = resolve_path(directory)
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=get_command_timeout(),
    )


def git_status(directory: str = ".") -> str:
    """Return git status for a repository."""

    try:
        result = _run_git(["status", "--short", "--branch"], directory)
        if result.returncode != 0:
            return tool_result(False, error=result.stderr.strip() or "Git command failed.")
        return tool_result(True, directory=str(resolve_path(directory)), status=result.stdout.strip())
    except FileNotFoundError:
        return tool_result(False, error="Git is not installed or not on PATH.")
    except subprocess.TimeoutExpired:
        return tool_result(False, error="Git command timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def git_log(directory: str = ".", max_count: int = 10) -> str:
    """Return recent git commit history."""

    try:
        result = _run_git(
            ["log", f"-{max_count}", "--oneline", "--decorate"],
            directory,
        )
        if result.returncode != 0:
            return tool_result(False, error=result.stderr.strip() or "Git command failed.")
        return tool_result(True, directory=str(resolve_path(directory)), log=result.stdout.strip())
    except FileNotFoundError:
        return tool_result(False, error="Git is not installed or not on PATH.")
    except subprocess.TimeoutExpired:
        return tool_result(False, error="Git command timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def git_diff(directory: str = ".", staged: bool = False) -> str:
    """Return git diff for a repository."""

    try:
        args = ["diff"]
        if staged:
            args.append("--staged")
        result = _run_git(args, directory)
        if result.returncode != 0:
            return tool_result(False, error=result.stderr.strip() or "Git command failed.")
        return tool_result(True, directory=str(resolve_path(directory)), diff=result.stdout.strip())
    except FileNotFoundError:
        return tool_result(False, error="Git is not installed or not on PATH.")
    except subprocess.TimeoutExpired:
        return tool_result(False, error="Git command timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
