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
- Use search_text when the user wants to find where something is referenced, used,
  imported, or mentioned INSIDE file contents (e.g. "where is X referenced/used/called",
  "search for Y in the code"). This searches file contents, not file names.
- Use search_files only when the user wants to find files BY NAME or extension pattern
  (e.g. "find all .json files", "list files named test_*"). This matches file names only
  and does not look inside file contents — it will NOT tell you where a symbol is used.
- If unsure whether the user wants a file-name match or a content match, prefer
  search_text — most "find/search for X" requests mean "find where X appears in code".
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
    """Resolve the workspace boundary that write/dangerous tools are restricted to.

    Defaults to ROOT_DIR — the directory this project was cloned/downloaded into,
    auto-derived from this file's own location (Path(__file__).resolve().parent) —
    so the workspace is portable across machines with zero configuration. Anyone who
    clones this repo and runs `python CLIagent.py` gets a workspace rooted at wherever
    they put it, not a path baked in by whoever wrote policy.json.

    An explicit "workspace_subpath" in config/policy.json still overrides this, for
    users who want the agent to operate on a different folder than the repo itself:
      - an absolute path is used as-is
      - a relative path is resolved under the user's home directory (Path.home())
    Leave "workspace_subpath" unset (or empty) to keep the portable default.
    """
    subpath = POLICY_CONFIG.get("workspace_subpath")
    if not subpath:
        return ROOT_DIR
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
