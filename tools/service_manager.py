"""Windows service management tools."""

import subprocess
import sys

from tools.path_utils import tool_result


def _run_sc(args: list) -> tuple[int, str, str]:
    """Run Windows 'sc' command."""
    try:
        result = subprocess.run(
            ["sc.exe", *args],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return -1, "", "sc.exe not found."
    except subprocess.TimeoutExpired:
        return -2, "", "Command timed out."
    except Exception as exc:
        return -3, "", str(exc)


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def list_services() -> str:
    """List all Windows services."""
    if not is_windows():
        return tool_result(False, error="Service management is only available on Windows.")

    try:
        returncode, stdout, stderr = _run_sc(["query", "type=", "service", "state=", "all"])

        if returncode != 0:
            return tool_result(False, error=stderr or "Failed to list services.")

        # Parse service names from output
        services = []
        for line in stdout.split("\n"):
            line = line.strip()
            if line.startswith("SERVICE_NAME:"):
                service_name = line.replace("SERVICE_NAME:", "").strip()
                services.append(service_name)

        return tool_result(
            True,
            count=len(services),
            services=services,
            output=stdout,
        )
    except Exception as exc:
        return tool_result(False, error=str(exc))


def get_service_status(service_name: str) -> str:
    """Get status of a Windows service."""
    if not is_windows():
        return tool_result(False, error="Service management is only available on Windows.")

    if not service_name.strip():
        return tool_result(False, error="Service name must not be empty.")

    try:
        returncode, stdout, stderr = _run_sc(["query", service_name.strip()])

        if returncode != 0:
            return tool_result(False, error=stderr or f"Service '{service_name}' not found.")

        # Parse status from output
        status = None
        for line in stdout.split("\n"):
            if "STATE" in line:
                status = line.split(":", 1)[-1].strip()
                break

        return tool_result(
            True,
            service_name=service_name.strip(),
            status=status,
            output=stdout,
        )
    except Exception as exc:
        return tool_result(False, error=str(exc))


def start_service(service_name: str) -> str:
    """Start a Windows service."""
    if not is_windows():
        return tool_result(False, error="Service management is only available on Windows.")

    if not service_name.strip():
        return tool_result(False, error="Service name must not be empty.")

    try:
        returncode, stdout, stderr = _run_sc(["start", service_name.strip()])

        success = returncode == 0
        return tool_result(
            True,
            success=success,
            service_name=service_name.strip(),
            message=stdout or stderr,
        )
    except Exception as exc:
        return tool_result(False, error=str(exc))


def stop_service(service_name: str) -> str:
    """Stop a Windows service."""
    if not is_windows():
        return tool_result(False, error="Service management is only available on Windows.")

    if not service_name.strip():
        return tool_result(False, error="Service name must not be empty.")

    try:
        returncode, stdout, stderr = _run_sc(["stop", service_name.strip()])

        success = returncode == 0
        return tool_result(
            True,
            success=success,
            service_name=service_name.strip(),
            message=stdout or stderr,
        )
    except Exception as exc:
        return tool_result(False, error=str(exc))


def restart_service(service_name: str) -> str:
    """Restart a Windows service."""
    if not is_windows():
        return tool_result(False, error="Service management is only available on Windows.")

    if not service_name.strip():
        return tool_result(False, error="Service name must not be empty.")

    try:
        # First stop
        _run_sc(["stop", service_name.strip()])
        # Then start
        returncode, stdout, stderr = _run_sc(["start", service_name.strip()])

        success = returncode == 0
        return tool_result(
            True,
            success=success,
            service_name=service_name.strip(),
            message=stdout or stderr,
        )
    except Exception as exc:
        return tool_result(False, error=str(exc))
