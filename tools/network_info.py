"""Network diagnostics and information tools."""

import socket
import subprocess
import sys

from config import get_command_timeout
from tools.path_utils import tool_result


def _run_command(cmd: list, timeout: int = 5) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out."
    except FileNotFoundError:
        return -2, "", "Command not found."
    except Exception as exc:
        return -3, "", str(exc)


def network_info() -> str:
    """Get network configuration information."""
    try:
        hostname = socket.gethostname()
        fqdn = socket.getfqdn()

        try:
            local_ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            local_ip = "Unable to resolve"

        # Get all IP addresses
        ips = []
        try:
            all_ips = socket.gethostbyname_ex(hostname)
            ips = all_ips[2] if len(all_ips) > 2 else []
        except socket.gaierror:
            pass

        return tool_result(
            True,
            hostname=hostname,
            fqdn=fqdn,
            local_ip=local_ip,
            all_ips=ips,
        )
    except Exception as exc:
        return tool_result(False, error=str(exc))


def ping(host: str, count: int = 4) -> str:
    """Ping a host and return results."""
    if not host.strip():
        return tool_result(False, error="Host must not be empty.")

    try:
        # Windows uses -n, Unix uses -c
        count_param = "-n" if sys.platform == "win32" else "-c"
        cmd = ["ping", count_param, str(count), host.strip()]

        returncode, stdout, stderr = _run_command(cmd, timeout=10)

        if returncode != 0:
            return tool_result(False, error=stderr or "Ping failed.")

        return tool_result(
            True,
            host=host.strip(),
            count=count,
            output=stdout,
        )
    except Exception as exc:
        return tool_result(False, error=str(exc))


def dns_lookup(hostname: str) -> str:
    """Resolve a hostname to IP address(es)."""
    if not hostname.strip():
        return tool_result(False, error="Hostname must not be empty.")

    try:
        hostname = hostname.strip()
        ips = socket.gethostbyname_ex(hostname)

        return tool_result(
            True,
            hostname=ips[0],
            aliases=ips[1],
            addresses=ips[2],
        )
    except socket.gaierror as exc:
        return tool_result(False, error=f"DNS lookup failed: {exc}")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def check_port(host: str, port: int, timeout: int = 5) -> str:
    """Check if a port is open on a host."""
    if not host.strip() or not isinstance(port, int) or port < 1 or port > 65535:
        return tool_result(False, error="Invalid host or port.")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host.strip(), port))
        sock.close()

        is_open = result == 0
        return tool_result(
            True,
            host=host.strip(),
            port=port,
            open=is_open,
            status="Open" if is_open else "Closed",
        )
    except socket.gaierror:
        return tool_result(False, error="Invalid hostname.")
    except Exception as exc:
        return tool_result(False, error=str(exc))
