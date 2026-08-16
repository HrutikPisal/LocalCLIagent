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
        "Create a NEW file in the workspace. Fails with an error if the path already "
        "exists — use this only when the file should not exist yet. To overwrite an "
        "existing file, or when you're not sure if it exists, use write_file instead. "
        "If this call's JSON result has success=false, NO write happened at all — the "
        "file's existing contents (whatever they were before this call) are unchanged. "
        "Do not state or imply what the file now contains after a failed call; only "
        "report the error, or call write_file/read_file if you need to actually change "
        "or check the content.",
        {
            "path": {"type": "string", "description": "File path to create."},
            "content": {"type": "string", "description": "Initial file content."},
        },
        required=["path"],
    ),
    _schema(
        "write_file",
        "Write content to a file in the workspace, creating it if it doesn't exist "
        "and OVERWRITING it without warning if it does. Use this to update/replace a "
        "file's contents. To create a file that must NOT already exist, use "
        "create_file instead, which fails safely if the path is already taken.",
        {
            "path": {"type": "string", "description": "File path."},
            "content": {"type": "string", "description": "Content to write."},
        },
        required=["path", "content"],
    ),
    _schema(
        "rename_file",
        "Rename a file within the workspace. Returns the exact new path as "
        "'destination' in its JSON result — when reporting the outcome, quote that "
        "field exactly; the old filename is no longer valid once this succeeds.",
        {
            "source": {"type": "string", "description": "Current file path."},
            "destination": {"type": "string", "description": "New file path."},
        },
        required=["source", "destination"],
    ),
    _schema(
        "copy_file",
        "Copy a file within the workspace. Returns the exact 'source' and "
        "'destination' paths in its JSON result — quote them exactly; both files "
        "exist after this succeeds, so do not conflate the two paths.",
        {
            "source": {"type": "string", "description": "Source file path."},
            "destination": {"type": "string", "description": "Destination file path."},
        },
        required=["source", "destination"],
    ),
    _schema(
        "move_file",
        "Move a file within the workspace. Returns the exact 'destination' path in "
        "its JSON result — when reporting the outcome, quote that field exactly. If "
        "this file was renamed or moved earlier in the conversation, any name used "
        "for it before this call is now stale; only this result's 'destination' is "
        "current.",
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
    _schema("pip_list", "List installed Python packages, as raw pip/JSON output. "
            "Equivalent to list_installed_packages — either works, this is just the "
            "shorter-named one.", {}),
    _schema(
        "pip_install",
        "Install a SINGLE named Python package with pip (e.g. 'requests' or "
        "'numpy==1.26'). Do NOT use this for installing everything listed in a "
        "requirements file — use install_requirements for that instead, since this "
        "tool takes one package name, not a file path.",
        {
            "package": {"type": "string", "description": "Package name to install, e.g. 'requests' or 'numpy==1.26'."},
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
        "Push commits to a remote git repository. Both remote and branch are "
        "optional — omit them to push the current branch to 'origin' (the default "
        "for both); only set them explicitly if the user names a different remote "
        "or branch.",
        {
            "directory": {"type": "string", "description": "Repository directory."},
            "remote": {"type": "string", "description": "Remote name (default: 'origin')."},
            "branch": {"type": "string", "description": "Branch name (default: current branch)."},
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
        "Run a command in a specific working directory, with accurate success/failure "
        "reporting (fails if the command's exit code is non-zero). Prefer this tool "
        "when cwd matters or you need to know whether the command actually succeeded. "
        "By default (shell=false) the command is split on whitespace, NOT parsed like "
        "a real shell — quoted arguments containing spaces will break; set shell=true "
        "to run it as a real shell command line instead (e.g. with pipes or quotes).",
        {
            "command": {"type": "string", "description": "Command to run, e.g. 'git status' or 'dir C:\\Users'."},
            "cwd": {"type": "string", "description": "Working directory to run the command in."},
            "shell": {"type": "boolean", "description": "Set true for shell syntax (pipes, quotes); false (default) does a naive whitespace split."},
        },
        required=["command"],
    ),
    _schema(
        "get_output",
        "Run a simple command and get back only its stdout text, nothing else. "
        "Always runs as a real shell command in the current working directory (no cwd "
        "parameter — cannot target a different folder). Treats a non-zero exit code as "
        "a tool failure with no output returned, so this is best for read-only "
        "commands you expect to succeed (e.g. 'python --version', 'echo %PATH%'), not "
        "for commands where you need to inspect stderr or a non-zero exit code.",
        {
            "command": {"type": "string", "description": "Command to execute, e.g. 'python --version'."},
        },
        required=["command"],
    ),
    _schema(
        "execute_command",
        "Run a shell command and get back full diagnostics: stdout, stderr, AND the "
        "return code, in a specific working directory. IMPORTANT: this tool always "
        "reports success at the top level even if the command itself failed — to know "
        "whether the command actually succeeded, check the 'return_code' field (0 "
        "means success) or the nested 'success' field in the result, not just the "
        "top-level result. Use this over get_output when you need stderr or the exit "
        "code, and over run_command when you need shell syntax like pipes or quotes.",
        {
            "command": {"type": "string", "description": "Command to execute."},
            "cwd": {"type": "string", "description": "Working directory to run the command in."},
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
        "Find processes whose name contains the given text — this is a "
        "case-insensitive SUBSTRING match, not an exact match (e.g. 'chrome' will "
        "also match 'chromedriver.exe'). If you need an exact single process, check "
        "the returned names/PIDs before acting on the result.",
        {
            "name": {"type": "string", "description": "Process name or substring to search for, e.g. 'python' or 'chrome'."},
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
        "Install a SINGLE named Python package with pip. Equivalent to pip_install — "
        "either works, this is just the alternate name. Do NOT use this for a "
        "requirements file; use install_requirements for that instead.",
        {
            "package": {"type": "string", "description": "Package name to install, e.g. 'requests' or 'numpy==1.26'."},
            "directory": {"type": "string", "description": "Project directory"},
        },
        required=["package"],
    ),
    _schema(
        "install_requirements",
        "Install ALL packages listed in a requirements file in one call — NOT for "
        "installing a single named package (use pip_install or install_package for "
        "that instead, they take a package name, not a file path). The path is "
        "required — there is no default. Typically this is 'requirements.txt' in the "
        "project root, but confirm the actual filename/location rather than assuming it.",
        {
            "requirements_file": {"type": "string", "description": "Path to the requirements file, typically 'requirements.txt'."},
            "directory": {"type": "string", "description": "Project directory"},
        },
        required=["requirements_file"],
    ),
    _schema(
        "list_installed_packages",
        "List all installed Python packages. Equivalent to pip_list — either works, "
        "this is just the longer-named one.",
        {},
    ),
]
