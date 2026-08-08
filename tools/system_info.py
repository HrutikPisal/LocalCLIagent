import platform
import sys

from tools.path_utils import tool_result


def _get_windows_version() -> str:
    """Detect Windows version correctly based on build number."""
    try:
        wv = sys.getwindowsversion()
        major, minor, build = wv.major, wv.minor, wv.build

        if major == 10 and minor == 0:
            if build >= 22000:
                return "Windows 11"
            else:
                return "Windows 10"
        elif major == 11:
            return "Windows 11"
        elif major == 10:
            return "Windows 10"
        else:
            return f"Windows {major}.{minor}"
    except AttributeError:
        return platform.system()


def system_info() -> str:
    """Return OS, CPU, memory, and Python environment information."""

    try:
        import psutil
    except ImportError:
        psutil = None

    info = {
        "os": platform.system(),
        "os_name": _get_windows_version() if platform.system() == "Windows" else platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "cwd": str(__import__("pathlib").Path.cwd()),
    }

    if psutil:
        vm = psutil.virtual_memory()
        info["cpu_count"] = psutil.cpu_count(logical=True)
        info["ram_total_gb"] = round(vm.total / (1024 ** 3), 2)
        info["ram_available_gb"] = round(vm.available / (1024 ** 3), 2)
        info["ram_used_percent"] = vm.percent
    else:
        info["note"] = "Install psutil for detailed CPU/RAM stats."

    return tool_result(True, **info)
