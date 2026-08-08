import subprocess

from config import get_command_timeout
from tools.path_utils import resolve_path, tool_result


def git_commit(directory: str = ".", message: str = "") -> str:
    """Create a git commit with the given message."""

    if not message.strip():
        return tool_result(False, error="Commit message is required.")

    try:
        cwd = resolve_path(directory)
        add_result = subprocess.run(
            ["git", "add", "-A"],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=get_command_timeout(),
        )
        if add_result.returncode != 0:
            return tool_result(False, error=add_result.stderr.strip() or "git add failed.")

        commit_result = subprocess.run(
            ["git", "commit", "-m", message.strip()],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=get_command_timeout(),
        )
        if commit_result.returncode != 0:
            return tool_result(False, error=commit_result.stderr.strip() or "git commit failed.")

        return tool_result(
            True,
            directory=str(cwd),
            message=message.strip(),
            output=commit_result.stdout.strip(),
        )
    except FileNotFoundError:
        return tool_result(False, error="Git is not installed or not on PATH.")
    except subprocess.TimeoutExpired:
        return tool_result(False, error="Git command timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def git_push(directory: str = ".", remote: str = "origin", branch: str = "") -> str:
    """Push commits to a remote git repository."""

    try:
        cwd = resolve_path(directory)
        args = ["git", "push", remote]
        if branch.strip():
            args.append(branch.strip())

        result = subprocess.run(
            args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=get_command_timeout() * 2,
        )
        if result.returncode != 0:
            return tool_result(False, error=result.stderr.strip() or "git push failed.")

        return tool_result(
            True,
            directory=str(cwd),
            remote=remote,
            branch=branch or "default",
            output=result.stdout.strip() or result.stderr.strip(),
        )
    except FileNotFoundError:
        return tool_result(False, error="Git is not installed or not on PATH.")
    except subprocess.TimeoutExpired:
        return tool_result(False, error="Git push timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
