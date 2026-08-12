"""Utility functions for tool operations."""

from tools.path_utils import tool_result


def get_tool_info() -> str:
    """Return information about available tools."""
    tools_info = {
        "filesystem": [
            "read_directory",
            "read_file",
            "create_file",
            "write_file",
            "edit_file",
            "rename_file",
            "copy_file",
            "move_file",
            "delete_file",
        ],
        "search": [
            "search_files",
            "search_text",
        ],
        "git": [
            "git_status",
            "git_log",
            "git_diff",
            "git_commit",
            "git_push",
        ],
        "python": [
            "run_python",
            "run_script",
            "pip_list",
            "pip_install",
        ],
        "system": [
            "system_info",
            "network_info",
            "process_manager",
            "service_manager",
        ],
    }
    return tool_result(True, tools=tools_info)
