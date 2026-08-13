# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Quick Start

### Run the Agent
```bash
python CLIagent.py
```
Starts the CLI agent. Ollama must be running or the agent will attempt to start it automatically.

**Agent Controls:**
- Type a question and press Enter to ask the agent
- **Windows, native console** (cmd.exe / PowerShell / Windows Terminal launched directly):
  press **Ctrl+X** OR type `.stop` to cancel the current turn
- **VSCode integrated terminal, Git Bash/MinTTY, or any other pty/ConPTY-relayed
  terminal**: type `.stop` — Ctrl+X may silently fail to register here (see comment
  block above the `msvcrt` import in [ollama_client.py](ollama_client.py) for why)
- Either way, cancellation now takes effect mid-generation, not just after the full
  response finishes — `_complete_turn()` streams the model response (`stream=True`) and
  checks the cancel flag after every chunk instead of blocking on the whole reply
- Type `exit` or `quit` to close the agent gracefully
- Press Ctrl+C to exit the agent completely and immediately

### Run Tests
```bash
# New tools smoke tests (no dependencies)
python test_new_tools.py

# Full evaluation (requires Ollama running)
python tests/smoke_tests.py
```

### Add a New Tool
Tools follow a strict pattern. To add a new tool:

1. **Create** `tools/tool_name.py`:
```python
from tools.path_utils import tool_result

def tool_function(arg: str) -> str:
    """One-line description."""
    try:
        # Implementation
        return tool_result(True, field=value)
    except Exception as exc:
        return tool_result(False, error=str(exc))
```

2. **Register** in `tool_registry.py`:
   - Add import: `from tools.tool_name import tool_function`
   - Add to `TOOL_MAP` with permission level (read, workspace_write, system_write, dangerous)
   - Add schema to `TOOLS_SCHEMA` describing parameters

3. **Test** the function in isolation before registering.

See [documents/TOOLS_IMPLEMENTATION_SUMMARY.md](documents/TOOLS_IMPLEMENTATION_SUMMARY.md) for examples of 8 recently added tools.

---

## Architecture Overview

### High-Level Data Flow

```
User Input (CLI)
    ↓
CLIagent.py (entry point)
    ↓
OllamaClient (sends to LLM, handles tool calls)
    ↓
ToolExecutor (dispatch)
    ├─ PolicyEngine (permission check)
    ├─ Tool function (execute)
    └─ AgentLogger (record activity)
    ↓
LLM processes tool output
    ↓
Response to user
```

### Core Responsibilities

**CLIagent.py** (19 lines)
- Entry point only; initializes conversation and agent
- Calls `ensure_ollama_ready()` for automatic setup

**OllamaClient** (83 lines)
- Sends messages to Ollama; receives responses
- Parses tool calls from LLM output
- No business logic; delegates to ToolExecutor

**Conversation** (25 lines)
- Maintains message history in Ollama format
- Methods: `add_user()`, `add_assistant()`, `add_tool()`, `add_assistant_tool_calls()`
- Injects system prompt on creation

**ToolExecutor** (80 lines)
- Executes tools after policy checks
- Delegates approval prompts to PolicyEngine
- Logs execution to AgentLogger
- Does NOT make permission decisions

**PolicyEngine** (100 lines)
- Evaluates tool calls: ALLOW, DENY, REQUIRE_APPROVAL
- Checks dangerous patterns, protected paths, workspace boundaries
- Decisions based on permission level + arguments, not tool name

**AgentLogger** (65 lines)
- Logs user prompts, tool execution, responses, timing
- Full raw output logged (not truncated)
- Structured JSON to `logs/agent.log`

**tool_registry.py** (284 lines)
- TOOL_MAP: Maps tool names to functions + metadata (permission, category)
- TOOLS_SCHEMA: OpenAI-format schemas for LLM tool selection
- Single source of truth for all available tools

---

## Tool System Design

### Tool Pattern

Every tool:
1. **Accepts** simple Python types (str, int, dict)
2. **Returns** JSON string via `tool_result(success: bool, **fields)`
3. **Never** prints output (logging only)
4. **Never** trusts user input (always validate paths, commands)
5. **Single responsibility** (read_file only reads, never modifies)

### Example: Three Tool Types

**Read-only** (auto-approved):
```python
def read_file(path: str) -> str:
    file_path = resolve_path(path)
    if not file_path.exists():
        return tool_result(False, error="File not found")
    return tool_result(True, path=str(file_path), content=file_path.read_text())
```

**Workspace write** (requires approval):
```python
def create_file(path: str, content: str) -> str:
    file_path = resolve_path(path)
    if not is_inside_workspace(file_path):
        return tool_result(False, error="Outside workspace")
    file_path.write_text(content)
    return tool_result(True, path=str(file_path))
```

**Dangerous** (requires typed approval):
```python
def delete_file(path: str) -> str:
    file_path = resolve_path(path)
    if is_protected_path(file_path):
        return tool_result(False, error="Protected path")
    file_path.unlink()
    return tool_result(True, path=str(file_path), message="Deleted")
```

### Path Utilities

Always use `tools/path_utils.py`:
- `resolve_path(user_input)` — Expands vars, resolves to absolute, handles "."
- `is_protected_path(path)` — Checks Windows, System32, AppData, etc.
- `is_inside_workspace(path)` — Enforces workspace boundary
- `tool_result(success, **payload)` — Returns JSON

---

## Permission System

### Permission Levels (PolicyEngine)

| Level | Auto-approve? | Use Case |
|-------|---------------|----------|
| `read` | YES | file/folder access, searches, git status, system info |
| `workspace_write` | NO (user approval) | create/edit/rename/copy/move files in workspace |
| `system_write` | NO (user approval) | pip install, git commit/push, run scripts |
| `dangerous` | NO (user approval) | delete files, process kill |

### Policy Checks (in order)

1. **Dangerous patterns**: Blocks substrings (format, shutdown, taskkill, etc.)
2. **Protected paths**: Blocks writes to Windows, System32, AppData, Program Files
3. **Workspace boundary**: Blocks workspace_write outside configured workspace root (currently: `E:\My Projects\local_cli_agent`)
4. **Permission level**: Determines if auto-approved or requires user confirmation

### Configuration

**config/policy.json**:
```json
{
  "workspace_subpath": "Projects",
  "protected_path_names": ["Windows", "System32", "AppData"],
  "dangerous_patterns": ["format", "shutdown", "taskkill"],
  "max_file_read_bytes": 1048576,
  "command_timeout_seconds": 30
}
```

---

## Configuration & Setup

### Models

**config/models.json**:
```json
{
  "default": "qwen2.5:3b",
  "allowed": ["qwen2.5:0.5b", "qwen2.5:1.5b", "qwen2.5:3b"]
}
```

Change default model to switch LLM. Current default (3B) is tuned for hallucination resistance via:
- Injected model identity in system prompt
- Explicit grounding rules forbidding invention
- Full raw output logging for audit trails

### Automatic Ollama Setup

**ollama_setup.py** handles:
- Detecting if Ollama server is running
- Starting Ollama if installed but not running
- Checking if model is downloaded
- Pulling model if missing
- Proper timeout and error handling

Users just run `python CLIagent.py` — setup is automatic.

---

## Common Development Tasks

### Add a New Tool Endpoint

Most common task. See "Add a New Tool" section above, then:

```bash
python -c "from tool_registry import TOOL_MAP; print(len(TOOL_MAP))"  # Verify registration
python test_new_tools.py  # Runs new tool tests
```

### Add a Tool with File System Access

Use `resolve_path()` + `is_protected_path()` + `is_inside_workspace()` from path_utils.

```python
from tools.path_utils import resolve_path, is_inside_workspace, tool_result

def my_tool(path: str) -> str:
    file_path = resolve_path(path)
    if not file_path.exists():
        return tool_result(False, error="Not found")
    if not is_inside_workspace(file_path):
        return tool_result(False, error="Outside workspace")
    # Proceed with file operations
    return tool_result(True, result="...")
```

### Debug a Tool

Add print statements in the tool function (stdout captured in logs), or:

```bash
python -c "
from tools.read_file import read_file
import json
result = json.loads(read_file('path/to/file.txt'))
print(json.dumps(result, indent=2))
"
```

### Check Current Tool Count

```bash
python -c "from tool_registry import TOOL_MAP; print(f'Registered tools: {len(TOOL_MAP)}')"
```

Expected: 56 tools (after registering the 8 newly implemented tools)

### Verify No Regressions

```bash
python tests/smoke_tests.py  # Full suite (requires Ollama)
python test_new_tools.py     # Just new tools (isolated)
```

---

## Current Project Status

**Completion**: 87% (as of August 8, 2026)

### What's Done ✅
- 9 core architecture files (100%)
- 36 tools implemented (95% — 8 need registry registration)
- 27 tests passing (100%)
- Complete documentation (11 files)

### What's Needed ⏳
- Register 8 new tools in tool_registry.py (30 min)
- Delete 5 redundant empty files (5 min)
- Update README with new tool list (30 min)

### What's Deferred to Phase 3
- Voice input/output module (40 hours, planned)

See [documents/CODEBASE_AUDIT.md](documents/CODEBASE_AUDIT.md) for complete audit or [documents/CLEANUP_ACTION_PLAN.md](documents/CLEANUP_ACTION_PLAN.md) for immediate next steps.

---

## Key Constraints & Patterns

### No Shell Access
The LLM has no access to arbitrary shell commands. Only registered tools are available. This is intentional and enforced by PolicyEngine.

If a task needs shell execution, create a tool wrapper:
```python
# In tools/terminal_read.py
def run_command(command: str) -> str:
    # Validates command, enforces timeout
    # LLM cannot execute dangerous commands
```

### Single Message Role Per Tool
When a tool is executed, add EXACTLY one message:
```python
conversation.add_tool(tool_name, output)
```

Do NOT mix tool messages in assistant responses. The message format matters for LLM understanding.

### Tool Output is JSON
Every tool returns JSON via `tool_result()`. This ensures:
- Consistent parsing by OllamaClient
- Structured logging
- Clear success/failure semantics
- No ambiguous string output

### Imports in tool_registry.py Only
Tools are imported ONLY in `tool_registry.py`. Main code imports `TOOL_MAP` and `TOOLS_SCHEMA`, not individual tools. This keeps initialization clear and centralized.

---

## File Organization

### Core (9 files, 728 LOC)
- `CLIagent.py`, `config.py`, `conversation.py`, `ollama_client.py`, `ollama_setup.py`, `tool_executor.py`, `policy_engine.py`, `logger.py`, `tool_registry.py`

### Tools (24 files, 843 LOC — 36 functions)
- Filesystem: read, write, create, delete, rename, copy, move, edit, search (9 functions across 5 files)
- Git: status, log, diff, commit, push (5 functions across 2 files)
- Python: run_python, run_script (2 functions in 1 file)
- Packages: pip_install, pip_list, install_requirements (3 functions across 2 files)
- Network: network_info, ping, dns_lookup, check_port (4 functions in 1 file) **NEW**
- Process: list, info, find, kill (4 functions in 1 file) **NEW**
- Services: list, status, start, stop, restart (5 functions in 1 file) **NEW**
- Terminal: run, get_output, execute (3 functions in 1 file) **NEW**
- System: system_info (1 function in 1 file)
- Discovery: get_tool_info (1 function in 1 file) **NEW**

### Config (2 files)
- `config/models.json` — LLM model selection
- `config/policy.json` — Security policies

### Tests (6 files)
- `test_new_tools.py` — Isolated tests for 8 new tools (14 tests, all passing)
- `tests/smoke_tests.py` — Full evaluation suite (requires Ollama)
- `tests/cli_agent_evaluation_dataset.json` — 50+ test cases

### Documentation (11 files)
- `CODEBASE_AUDIT.md` — Complete audit with findings
- `CLEANUP_ACTION_PLAN.md` — Step-by-step next steps
- `AUDIT_CONCLUSIONS.md` — Conclusions and recommendations
- `TOOLS_IMPLEMENTATION_SUMMARY.md` — Details on 8 new tools
- Plus: README, plan, feature summaries, setup guides

---

## Debugging Tips

### "Tool not in TOOL_MAP" error
- Tool wasn't registered in `tool_registry.py`
- Verify: imports at top, entry in TOOL_MAP, entry in TOOLS_SCHEMA
- Check: `python tool_registry.py` loads without errors

### "Permission denied" when tool should work
- Check `PolicyEngine.evaluate()` in policy_engine.py
- Print arguments being evaluated: `print(tool_name, arguments, tool_entry)`
- Check config/policy.json for dangerous_patterns or protected_path_names
- Use `is_inside_workspace()` to debug path issues

### Tool returns success=false with unexpected error
- Errors are captured as `error` field in tool_result
- Check: path validation, file existence, permissions
- Examine error message returned to user

### "Timeout" during tool execution
- Default timeout is 30 seconds (config/policy.json)
- Long-running commands (pip install, git clone) may exceed
- Increase `command_timeout_seconds` if needed

---

## Code Review Checklist (for new tools)

When adding a tool, verify:

- ✅ Function signature: `def tool_name(args: types) -> str`
- ✅ Return type: JSON from `tool_result(success, **kwargs)`
- ✅ Error handling: All exceptions caught, returned as `tool_result(False, error=...)`
- ✅ Path validation: Uses `resolve_path()`, `is_protected_path()`, `is_inside_workspace()`
- ✅ Registered in tool_registry.py: imports + TOOL_MAP + TOOLS_SCHEMA
- ✅ Permission level: Correct for the operation (read, workspace_write, system_write, dangerous)
- ✅ Docstring: One-line description of what it does
- ✅ Tests: Function tested in test_new_tools.py or isolated test

---

## References

- **Architecture Plan**: [documents/plan.md](documents/plan.md)
- **Feature Summary**: [documents/FEATURE_SUMMARY.md](documents/FEATURE_SUMMARY.md)
- **New Tools Details**: [documents/TOOLS_IMPLEMENTATION_SUMMARY.md](documents/TOOLS_IMPLEMENTATION_SUMMARY.md)
- **Workspace Setup**: [documents/WORKSPACE_CONFIGURATION.md](documents/WORKSPACE_CONFIGURATION.md)
- **Quick Audit**: [documents/AUDIT_QUICK_REFERENCE.txt](documents/AUDIT_QUICK_REFERENCE.txt)
- **Detailed Audit**: [documents/CODEBASE_AUDIT.md](documents/CODEBASE_AUDIT.md)
- **Audit Conclusions**: [documents/AUDIT_CONCLUSIONS.md](documents/AUDIT_CONCLUSIONS.md)
- **Next Steps**: [documents/CLEANUP_ACTION_PLAN.md](documents/CLEANUP_ACTION_PLAN.md)

