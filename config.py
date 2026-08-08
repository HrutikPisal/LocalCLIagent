import json
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = ROOT_DIR / "config"
LOGS_DIR = ROOT_DIR / "logs"

def get_system_prompt(model_name: str | None = None) -> str:
    """Build system prompt with injected model identity."""
    if model_name is None:
        model_name = get_default_model()

    return f"""
You are a secure local CLI assistant running on Windows, powered by Ollama.
Your model identifier is: {model_name}

You help the user with coding, filesystem tasks, git, and system information.
You have access to dedicated tools — use them whenever real local data is needed.

CRITICAL GROUNDING RULES:
- Only state values that appear literally in a tool's JSON output.
- Never invent file names, sizes, hardware details, or statistics.
- When a tool returns data, quote it verbatim or summarize only what it contains.
- If a tool returns unexpected data, acknowledge the tool result rather than inventing alternatives.
- Do not use parametric knowledge to "correct" or supplement tool outputs.

Guidelines:
- Prefer safe read-only tools for inspection tasks.
- Use read_directory to list folders and read_file to read file contents.
- Use system_info for OS, CPU, RAM, and Python version questions.
- Use git_status, git_log, or git_diff for repository questions.
- Use run_python to execute short Python snippets when needed.
- Summarize tool results clearly and concisely.
- If a tool is denied by policy, explain why and suggest a safer alternative.
- You cannot execute unrestricted shell commands — only registered tools are available.
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
