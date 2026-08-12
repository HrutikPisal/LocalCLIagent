from tools.create_file import create_file
from tools.delete_file import copy_file, delete_file, move_file, rename_file
from tools.git_status import git_diff, git_log, git_status
from tools.git_write import git_commit, git_push
from tools.pip_tools import pip_install, pip_list
from tools.python_runner import run_python, run_script
from tools.read_directory import read_directory
from tools.read_file import read_file
from tools.search_files import search_files
from tools.search_text import search_text
from tools.system_info import system_info
from tools.write_file import write_file
from tools.tools import get_tool_info
from tools.network_info import network_info, ping, dns_lookup, check_port
from tools.edit_file import edit_file, insert_line, delete_line
from tools.terminal_read import run_command as terminal_run_command, get_output, execute_command
from tools.process_manager import list_processes, find_process_by_name, get_process_info, kill_process
from tools.service_manager import list_services, get_service_status, start_service, stop_service, restart_service
from tools.install_package import install_package, install_requirements, list_installed_packages


def _schema(name: str, description: str, properties: dict, required: list | None = None) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required or [],
            },
        },
    }


TOOL_MAP = {
    "read_directory": {
        "function": read_directory,
        "permission": "read",
        "category": "filesystem",
    },
    "read_file": {
        "function": read_file,
        "permission": "read",
        "category": "filesystem",
    },
    "search_files": {
        "function": search_files,
        "permission": "read",
        "category": "search",
    },
    "search_text": {
        "function": search_text,
        "permission": "read",
        "category": "search",
    },
    "system_info": {
        "function": system_info,
        "permission": "read",
        "category": "system",
    },
    "git_status": {
        "function": git_status,
        "permission": "read",
        "category": "git",
    },
    "git_log": {
        "function": git_log,
        "permission": "read",
        "category": "git",
    },
    "git_diff": {
        "function": git_diff,
        "permission": "read",
        "category": "git",
    },
    "run_python": {
        "function": run_python,
        "permission": "read",
        "category": "python",
    },
    "run_script": {
        "function": run_script,
        "permission": "system_write",
        "category": "python",
    },
    "create_file": {
        "function": create_file,
        "permission": "workspace_write",
        "category": "filesystem",
    },
    "write_file": {
        "function": write_file,
        "permission": "workspace_write",
        "category": "filesystem",
    },
    "rename_file": {
        "function": rename_file,
        "permission": "workspace_write",
        "category": "filesystem",
    },
    "copy_file": {
        "function": copy_file,
        "permission": "workspace_write",
        "category": "filesystem",
    },
    "move_file": {
        "function": move_file,
        "permission": "workspace_write",
        "category": "filesystem",
    },
    "delete_file": {
        "function": delete_file,
        "permission": "dangerous",
        "category": "filesystem",
    },
    "pip_list": {
        "function": pip_list,
        "permission": "read",
        "category": "package",
    },
    "pip_install": {
        "function": pip_install,
        "permission": "system_write",
        "category": "package",
    },
    "git_commit": {
        "function": git_commit,
        "permission": "system_write",
        "category": "git",
    },
    "git_push": {
        "function": git_push,
        "permission": "system_write",
        "category": "git",
    },
    "get_tool_info": {
        "function": get_tool_info,
        "permission": "read",
        "category": "system",
    },
    "network_info": {
        "function": network_info,
        "permission": "read",
        "category": "system",
    },
    "ping": {
        "function": ping,
        "permission": "read",
        "category": "system",
    },
    "dns_lookup": {
        "function": dns_lookup,
        "permission": "read",
        "category": "system",
    },
    "check_port": {
        "function": check_port,
        "permission": "read",
        "category": "system",
    },
    "edit_file": {
        "function": edit_file,
        "permission": "workspace_write",
        "category": "filesystem",
    },
    "insert_line": {
        "function": insert_line,
        "permission": "workspace_write",
        "category": "filesystem",
    },
    "delete_line": {
        "function": delete_line,
        "permission": "workspace_write",
        "category": "filesystem",
    },
    "run_command": {
        "function": terminal_run_command,
        "permission": "workspace_write",
        "category": "terminal",
    },
    "get_output": {
        "function": get_output,
        "permission": "workspace_write",
        "category": "terminal",
    },
    "execute_command": {
        "function": execute_command,
        "permission": "workspace_write",
        "category": "terminal",
    },
    "list_processes": {
        "function": list_processes,
        "permission": "read",
        "category": "system",
    },
    "find_process_by_name": {
        "function": find_process_by_name,
        "permission": "read",
        "category": "system",
    },
    "get_process_info": {
        "function": get_process_info,
        "permission": "read",
        "category": "system",
    },
    "kill_process": {
        "function": kill_process,
        "permission": "dangerous",
        "category": "system",
    },
    "list_services": {
        "function": list_services,
        "permission": "read",
        "category": "system",
    },
    "get_service_status": {
        "function": get_service_status,
        "permission": "read",
        "category": "system",
    },
    "start_service": {
        "function": start_service,
        "permission": "system_write",
        "category": "system",
    },
    "stop_service": {
        "function": stop_service,
        "permission": "system_write",
        "category": "system",
    },
    "restart_service": {
        "function": restart_service,
        "permission": "system_write",
        "category": "system",
    },
    "install_package": {
        "function": install_package,
        "permission": "system_write",
        "category": "package",
    },
    "install_requirements": {
        "function": install_requirements,
        "permission": "system_write",
        "category": "package",
    },
    "list_installed_packages": {
        "function": list_installed_packages,
        "permission": "read",
        "category": "package",
    },
}


TOOLS_SCHEMA = [
    _schema(
        "read_directory",
        "List files and folders inside a directory.",
        {"directory": {"type": "string", "description": "Directory path (default: current directory)."}},
    ),
    _schema(
        "read_file",
        "Read the contents of a text file.",
        {"path": {"type": "string", "description": "Path to the file."}},
        required=["path"],
    ),
    _schema(
        "search_files",
        "Search for files matching a glob pattern.",
        {
            "directory": {"type": "string", "description": "Directory to search in."},
            "pattern": {"type": "string", "description": "Glob pattern, e.g. *.py"},
            "recursive": {"type": "boolean", "description": "Search recursively."},
        },
    ),
    _schema(
        "search_text",
        "Search for text inside files.",
        {
            "directory": {"type": "string", "description": "Directory to search in."},
            "query": {"type": "string", "description": "Text to find."},
            "file_pattern": {"type": "string", "description": "File glob pattern."},
        },
        required=["query"],
    ),
    _schema("system_info", "Get OS, CPU, RAM, and Python version information.", {}),
    _schema(
        "git_status",
        "Show git status for a repository.",
        {"directory": {"type": "string", "description": "Repository directory."}},
    ),
    _schema(
        "git_log",
        "Show recent git commits.",
        {
            "directory": {"type": "string", "description": "Repository directory."},
            "max_count": {"type": "integer", "description": "Number of commits to show."},
        },
    ),
    _schema(
        "git_diff",
        "Show git diff for a repository.",
        {
            "directory": {"type": "string", "description": "Repository directory."},
            "staged": {"type": "boolean", "description": "Show staged changes only."},
        },
    ),
    _schema(
        "run_python",
        "Execute a short Python snippet and return stdout/stderr.",
        {
            "code": {"type": "string", "description": "Python code to execute."},
            "directory": {"type": "string", "description": "Working directory context."},
        },
        required=["code"],
    ),
    _schema(
        "run_script",
        "Run a Python script file.",
        {
            "script_path": {"type": "string", "description": "Path to the .py script."},
            "directory": {"type": "string", "description": "Working directory."},
        },
        required=["script_path"],
    ),
    _schema(
        "create_file",
        "Create a new file in the workspace.",
        {
            "path": {"type": "string", "description": "File path to create."},
            "content": {"type": "string", "description": "Initial file content."},
        },
        required=["path"],
    ),
    _schema(
        "write_file",
        "Write content to a file in the workspace.",
        {
            "path": {"type": "string", "description": "File path."},
            "content": {"type": "string", "description": "Content to write."},
        },
        required=["path", "content"],
    ),
    _schema(
        "rename_file",
        "Rename a file within the workspace.",
        {
            "source": {"type": "string", "description": "Current file path."},
            "destination": {"type": "string", "description": "New file path."},
        },
        required=["source", "destination"],
    ),
    _schema(
        "copy_file",
        "Copy a file within the workspace.",
        {
            "source": {"type": "string", "description": "Source file path."},
            "destination": {"type": "string", "description": "Destination file path."},
        },
        required=["source", "destination"],
    ),
    _schema(
        "move_file",
        "Move a file within the workspace.",
        {
            "source": {"type": "string", "description": "Source file path."},
            "destination": {"type": "string", "description": "Destination file path."},
        },
        required=["source", "destination"],
    ),
    _schema(
        "delete_file",
        "Delete a file. Requires explicit approval.",
        {"path": {"type": "string", "description": "File path to delete."}},
        required=["path"],
    ),
    _schema("pip_list", "List installed Python packages.", {}),
    _schema(
        "pip_install",
        "Install a Python package using pip.",
        {
            "package": {"type": "string", "description": "Package name."},
            "directory": {"type": "string", "description": "Optional project directory."},
        },
        required=["package"],
    ),
    _schema(
        "git_commit",
        "Stage all changes and create a git commit.",
        {
            "directory": {"type": "string", "description": "Repository directory."},
            "message": {"type": "string", "description": "Commit message."},
        },
        required=["message"],
    ),
    _schema(
        "git_push",
        "Push commits to a remote git repository.",
        {
            "directory": {"type": "string", "description": "Repository directory."},
            "remote": {"type": "string", "description": "Remote name."},
            "branch": {"type": "string", "description": "Branch name."},
        },
    ),
    _schema(
        "get_tool_info",
        "Get information about all available tools.",
        {},
    ),
    _schema(
        "network_info",
        "Get hostname, FQDN, and IP address information.",
        {},
    ),
    _schema(
        "ping",
        "Ping a host to test connectivity.",
        {
            "host": {"type": "string", "description": "Hostname or IP address"},
            "count": {"type": "integer", "description": "Number of ping requests"},
        },
        required=["host"],
    ),
    _schema(
        "dns_lookup",
        "Resolve a hostname to IP address(es).",
        {
            "hostname": {"type": "string", "description": "Hostname to resolve"},
        },
        required=["hostname"],
    ),
    _schema(
        "check_port",
        "Check if a port is open on a host.",
        {
            "host": {"type": "string", "description": "Hostname or IP"},
            "port": {"type": "integer", "description": "Port number"},
            "timeout": {"type": "integer", "description": "Timeout in seconds"},
        },
        required=["host", "port"],
    ),
    _schema(
        "edit_file",
        "Find and replace text in a file.",
        {
            "path": {"type": "string", "description": "File path"},
            "find": {"type": "string", "description": "Text to find"},
            "replace": {"type": "string", "description": "Text to replace with"},
        },
        required=["path", "find", "replace"],
    ),
    _schema(
        "insert_line",
        "Insert a line at a specific line number.",
        {
            "path": {"type": "string", "description": "File path"},
            "line_number": {"type": "integer", "description": "Line number"},
            "content": {"type": "string", "description": "Content to insert"},
        },
        required=["path", "line_number", "content"],
    ),
    _schema(
        "delete_line",
        "Delete a line at a specific line number.",
        {
            "path": {"type": "string", "description": "File path"},
            "line_number": {"type": "integer", "description": "Line number"},
        },
        required=["path", "line_number"],
    ),
    _schema(
        "run_command",
        "Run a shell command and capture output.",
        {
            "command": {"type": "string", "description": "Command to run"},
            "cwd": {"type": "string", "description": "Working directory"},
            "shell": {"type": "boolean", "description": "Use shell mode"},
        },
        required=["command"],
    ),
    _schema(
        "get_output",
        "Execute a command and return only stdout.",
        {
            "command": {"type": "string", "description": "Command to execute"},
        },
        required=["command"],
    ),
    _schema(
        "execute_command",
        "Execute a shell command with full output capture.",
        {
            "command": {"type": "string", "description": "Command to execute"},
            "cwd": {"type": "string", "description": "Working directory"},
        },
        required=["command"],
    ),
    _schema(
        "list_processes",
        "List all running processes.",
        {},
    ),
    _schema(
        "find_process_by_name",
        "Find processes matching a name pattern.",
        {
            "name": {"type": "string", "description": "Process name to search"},
        },
        required=["name"],
    ),
    _schema(
        "get_process_info",
        "Get detailed information about a process.",
        {
            "pid": {"type": "integer", "description": "Process ID"},
        },
        required=["pid"],
    ),
    _schema(
        "kill_process",
        "Terminate a process. Requires approval.",
        {
            "pid": {"type": "integer", "description": "Process ID to terminate"},
        },
        required=["pid"],
    ),
    _schema(
        "list_services",
        "List all Windows services.",
        {},
    ),
    _schema(
        "get_service_status",
        "Get status of a Windows service.",
        {
            "service_name": {"type": "string", "description": "Service name"},
        },
        required=["service_name"],
    ),
    _schema(
        "start_service",
        "Start a Windows service.",
        {
            "service_name": {"type": "string", "description": "Service name"},
        },
        required=["service_name"],
    ),
    _schema(
        "stop_service",
        "Stop a Windows service.",
        {
            "service_name": {"type": "string", "description": "Service name"},
        },
        required=["service_name"],
    ),
    _schema(
        "restart_service",
        "Restart a Windows service.",
        {
            "service_name": {"type": "string", "description": "Service name"},
        },
        required=["service_name"],
    ),
    _schema(
        "install_package",
        "Install a package using pip.",
        {
            "package": {"type": "string", "description": "Package name"},
            "directory": {"type": "string", "description": "Project directory"},
        },
        required=["package"],
    ),
    _schema(
        "install_requirements",
        "Install packages from a requirements.txt file.",
        {
            "requirements_file": {"type": "string", "description": "Path to requirements.txt"},
            "directory": {"type": "string", "description": "Project directory"},
        },
        required=["requirements_file"],
    ),
    _schema(
        "list_installed_packages",
        "List all installed Python packages.",
        {},
    ),
]
