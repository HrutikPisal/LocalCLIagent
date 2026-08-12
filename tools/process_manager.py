"""Process management tools."""

import subprocess
import sys

from tools.path_utils import tool_result

try:
    import psutil
except ImportError:
    psutil = None


def list_processes() -> str:
    """List all running processes."""
    if not psutil:
        return tool_result(False, error="psutil not installed. Run 'pip install psutil'.")

    try:
        processes = []
        for proc in psutil.process_iter(["pid", "name", "status"]):
            try:
                processes.append({
                    "pid": proc.info["pid"],
                    "name": proc.info["name"],
                    "status": proc.info["status"],
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return tool_result(
            True,
            count=len(processes),
            processes=processes,
        )
    except Exception as exc:
        return tool_result(False, error=str(exc))


def get_process_info(pid: int) -> str:
    """Get detailed information about a process."""
    if not psutil:
        return tool_result(False, error="psutil not installed. Run 'pip install psutil'.")

    if not isinstance(pid, int) or pid < 0:
        return tool_result(False, error="PID must be a positive integer.")

    try:
        proc = psutil.Process(pid)

        info = {
            "pid": proc.pid,
            "name": proc.name(),
            "status": proc.status(),
            "ppid": proc.ppid(),
            "num_threads": proc.num_threads(),
            "create_time": proc.create_time(),
        }

        try:
            info["username"] = proc.username()
        except (psutil.AccessDenied, AttributeError):
            info["username"] = "N/A"

        try:
            info["cwd"] = proc.cwd()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            info["cwd"] = "N/A"

        try:
            mem = proc.memory_info()
            info["memory_rss_mb"] = round(mem.rss / (1024 * 1024), 2)
            info["memory_vms_mb"] = round(mem.vms / (1024 * 1024), 2)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

        return tool_result(True, process=info)

    except psutil.NoSuchProcess:
        return tool_result(False, error=f"Process {pid} not found.")
    except psutil.AccessDenied:
        return tool_result(False, error=f"Access denied to process {pid}.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def kill_process(pid: int) -> str:
    """Terminate a process by PID."""
    if not isinstance(pid, int) or pid < 0:
        return tool_result(False, error="PID must be a positive integer.")

    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                capture_output=True,
                timeout=5,
            )
        else:
            subprocess.run(
                ["kill", "-9", str(pid)],
                capture_output=True,
                timeout=5,
            )

        return tool_result(
            True,
            pid=pid,
            message=f"Process {pid} terminated.",
        )

    except subprocess.TimeoutExpired:
        return tool_result(False, error="Kill command timed out.")
    except Exception as exc:
        return tool_result(False, error=str(exc))


def find_process_by_name(name: str) -> str:
    """Find processes by name."""
    if not psutil:
        return tool_result(False, error="psutil not installed. Run 'pip install psutil'.")

    if not name.strip():
        return tool_result(False, error="Process name must not be empty.")

    try:
        name_lower = name.strip().lower()
        matches = []

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if name_lower in proc.info["name"].lower():
                    matches.append({
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return tool_result(
            True,
            search_name=name,
            count=len(matches),
            processes=matches,
        )
    except Exception as exc:
        return tool_result(False, error=str(exc))
