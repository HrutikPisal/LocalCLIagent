import json
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = ROOT_DIR / "config"
LOGS_DIR = ROOT_DIR / "logs"

def get_system_prompt(model_name: str | None = None) -> str:
    """Build system prompt with injected model identity and workspace info."""
    if model_name is None:
        model_name = get_default_model()

    workspace = get_workspace_root()

    return f"""
You are a secure local CLI assistant running on Windows, powered by Ollama.
Your model identifier is: {model_name}

You help the user with coding, filesystem tasks, git, and system information.
You have access to dedicated tools — use them ONLY when the user's request genuinely
requires real, current local data that you do not already have in this conversation.

WORKSPACE INFORMATION:
- Your working directory/workspace is: {workspace}
- You can create, read, modify, and delete files within this workspace
- All file paths should be relative to this workspace or full absolute paths within it
- Never attempt to create files outside this workspace directory

CRITICAL GROUNDING RULES:
- Only state values that appear literally in a tool's JSON output.
- Never invent file names, sizes, hardware details, or statistics.
- When a tool returns data, quote it verbatim or summarize only what it contains.
- If a tool returns unexpected data, acknowledge the tool result rather than inventing alternatives.
- Do not use parametric knowledge to "correct" or supplement tool outputs.

WHEN NOT TO USE TOOLS:
- Do NOT call any tool for greetings, small talk, thanks, or goodbyes (e.g. "Hello",
  "hi", "thanks", "how are you", "bye"). Reply directly and conversationally.
- Do NOT call any tool for questions you can already answer from this conversation's
  context (e.g. "what did I just ask you?", "what's your name?").
- Do NOT call a tool speculatively "just in case" — only call one when the user's
  wording clearly requires real, current local data (system specs, file contents,
  directory listings, git state, running processes, etc.) that you do not already have.

Guidelines:
- Only use read-only tools for inspection tasks when the user's request needs real data.
- Use read_directory to list folders and read_file to read file contents.
- Use system_info for OS, CPU, RAM, and Python version questions.
- Use git_status, git_log, or git_diff for repository questions.
- Use run_python to execute short Python snippets when needed.
- Summarize tool results clearly and concisely.
- If a tool is denied by policy, explain why and suggest a safer alternative.
- You cannot execute unrestricted shell commands — only registered tools are available.
- When a user asks to create/modify files without specifying a full path, create them in the workspace root or suggest a path within the workspace.
""".strip()

def _load_json(filename: str) -> dict:
    path = CONFIG_DIR / filename
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


MODELS_CONFIG = _load_json("models.json")
POLICY_CONFIG = _load_json("policy.json")


def get_default_model() -> str:
    return MODELS_CONFIG.get("default", "qwen2.5:1.5b-instruct")


def get_allowed_models() -> list[str]:
    return MODELS_CONFIG.get("allowed", [get_default_model()])


def get_workspace_root() -> Path:
    subpath = POLICY_CONFIG.get("workspace_subpath", "Projects")
    if Path(subpath).is_absolute():
        return Path(subpath)
    return Path.home() / subpath


def get_protected_path_names() -> list[str]:
    return POLICY_CONFIG.get(
        "protected_path_names",
        ["Windows", "Program Files", "Program Files (x86)", "System32", "AppData"],
    )


def get_dangerous_patterns() -> list[str]:
    return POLICY_CONFIG.get("dangerous_patterns", [])


def get_max_file_read_bytes() -> int:
    return int(POLICY_CONFIG.get("max_file_read_bytes", 1048576))


def get_max_python_output_chars() -> int:
    return int(POLICY_CONFIG.get("max_python_output_chars", 10000))


def get_command_timeout() -> int:
    return int(POLICY_CONFIG.get("command_timeout_seconds", 30))


# Backward compatibility for smoke_tests and older imports.
ALLOWED_MODELS = {
    "default": get_default_model(),
    "available": get_allowed_models(),
}
