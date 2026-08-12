"""Package installation utilities (wrapper around pip_tools)."""

from tools.pip_tools import pip_install, pip_list
from tools.path_utils import tool_result


def install_package(package: str, directory: str = ".") -> str:
    """Install a package using pip (alias for pip_install)."""
    return pip_install(package, directory)


def list_installed_packages() -> str:
    """List installed packages (alias for pip_list)."""
    return pip_list()


def install_requirements(requirements_file: str, directory: str = ".") -> str:
    """Install packages from a requirements.txt file."""
    if not requirements_file.strip():
        return tool_result(False, error="Requirements file path must not be empty.")

    import subprocess
    import sys
    from config import get_command_timeout
    from tools.path_utils import resolve_path

    try:
        req_path = resolve_path(requirements_file)

        if not req_path.exists():
            return tool_result(False, error="Requirements file not found.")

        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(req_path)],
            cwd=str(resolve_path(directory)),
            capture_output=True,
            text=True,
            timeout=get_command_timeout() * 5,
        )

        return tool_result(
            success=result.returncode == 0,
            requirements_file=str(req_path),
            stdout=result.stdout.strip(),
            stderr=result.stderr.strip(),
        )

    except subprocess.TimeoutExpired:
        return tool_result(False, error="Installation timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
