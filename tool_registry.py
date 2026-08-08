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
]
