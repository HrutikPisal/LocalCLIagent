# Local CLI Agent

A secure, modular local-first AI CLI assistant powered by **Ollama** and the **Qwen 2.5** language model. Designed for Windows, with extensible tool support and strict security policies.

## 🎯 Overview

**Local CLI Agent** is an initial prototype of a conversational terminal assistant that runs entirely on your local machine. It combines:

- **Local LLM**: Uses Ollama to run Qwen 2.5 models without cloud dependencies
- **Tool Integration**: Filesystem, Git, Python, and system tools with automatic selection
- **Security-First**: Permission-based policy engine blocks dangerous operations
- **Extensible Architecture**: Easy to add new tools and capabilities

**Key Vision**: Evolve from a simple CLI chatbot → secure coding assistant → voice-controlled AI OS.

## ⚡ Quick Start

### Prerequisites
- **Python 3.10+** installed (the code uses `str | None` union-type syntax, which
  requires 3.10 or newer — it will fail to import on 3.8/3.9)
- **Ollama** installed separately from [ollama.com](https://ollama.com) — `pip install`
  only installs the Python *client*, not the Ollama application/server itself
- **Git** (optional, for version control)
- A few GB of free disk space (for the pulled model) and ideally a few GB of free RAM —
  see the "Performance Notes" section further down for what to expect on modest hardware

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/LocalCLIagent.git
cd LocalCLIagent

# Install Python dependencies
pip install -r requirements.txt

# Start the agent (automatic setup)
python CLIagent.py
```

On first run, the agent will automatically:
- ✅ Detect if the Ollama server is running, and start it if it's installed but not running
- ✅ Pull the default model (`qwen2.5:3b`, ~2GB) if it isn't already downloaded — needs
  an internet connection and can take a few minutes
- ✅ Warn if available RAM looks too low for comfortable local inference
- ✅ Launch interactive chat, with the workspace boundary automatically set to wherever
  you cloned this repo — no configuration needed to start reading/writing files here

## 💬 Example Usage

```
[USER] > What Python version is installed?
[AGENT] Thinking...
[TOOL] Calling: system_info

[AGENT] The installed Python version is 3.11.3, located at C:\Program Files\Python311\python.exe.

[USER] > Show me the files in the current directory.
[AGENT] Thinking...
[TOOL] Calling: read_directory

[AGENT] The current directory contains: README.md, src/ (folder), and requirements.txt.

[USER] > exit
Goodbye.
```

### Controls

- Type **`.stop`** anytime to cancel the current turn without exiting the agent —
  useful since local inference on modest hardware can take anywhere from a few seconds
  to several minutes per response
- On Windows, in a native console (cmd.exe / PowerShell / Windows Terminal launched
  directly — **not** VSCode's integrated terminal or Git Bash), **Ctrl+X** also cancels
  the current turn
- Type `exit` or `quit` to close the agent gracefully
- Press **Ctrl+C** to exit immediately
- Write/dangerous operations (create, edit, delete, git commit/push, run scripts,
  install packages, etc.) always prompt for `[y/N]` approval first — nothing destructive
  happens silently

## 🛠️ Registered Tools

### Filesystem
- `read_directory` — List folder contents
- `read_file` — Read file content
- `create_file` — Create a new file
- `write_file` — Write/overwrite file
- `rename_file` — Rename a file
- `copy_file` — Copy a file
- `move_file` — Move a file
- `delete_file` — Delete a file (requires approval)
- `search_files` — Search by filename pattern
- `search_text` — Search text inside files

### Git
- `git_status` — Repository status
- `git_log` — Recent commits
- `git_diff` — Unstaged changes
- `git_commit` — Create a commit (requires approval)
- `git_push` — Push to remote (requires approval)

### Python & Packages
- `run_python` — Execute Python snippets (sandboxed)
- `run_script` — Run .py scripts (requires approval)
- `pip_list` — List installed packages
- `pip_install` — Install packages (requires approval)

### System
- `system_info` — OS, CPU, RAM, Python details

### Network & Diagnostics
- `network_info` — Get hostname and IP information
- `ping` — Test connectivity to a host
- `dns_lookup` — Resolve hostname to IP addresses
- `check_port` — Check if a port is open

### File Editing
- `edit_file` — Find and replace text in files
- `insert_line` — Insert a line at specific position
- `delete_line` — Delete a line at specific position

### Terminal & Execution
- `run_command` — Execute shell commands
- `get_output` — Execute and capture output
- `execute_command` — Execute with full output capture

### Process Management
- `list_processes` — List all running processes
- `find_process_by_name` — Search for processes
- `get_process_info` — Get process details
- `kill_process` — Terminate a process (requires approval)

### Windows Services
- `list_services` — List Windows services
- `get_service_status` — Get service status
- `start_service` — Start a service (requires approval)
- `stop_service` — Stop a service (requires approval)
- `restart_service` — Restart a service (requires approval)

### Package Utilities
- `install_package` — Install packages (requires approval)
- `install_requirements` — Install from requirements.txt (requires approval)
- `list_installed_packages` — List installed packages

### Tools Discovery
- `get_tool_info` — Get information about all available tools

## 🔐 Permission Levels

| Level | Tools | Approval |
|-------|-------|----------|
| **Read** | File/folder access, search, git status, system info | Auto |
| **Workspace Write** | Create/edit/rename/copy/move files | User approval |
| **System Write** | Install packages, commit, push, run scripts | User approval |
| **Dangerous** | Delete files | User approval + typed confirmation |

**Workspace**: Restricted to the project's own directory by default — auto-detected from
wherever you cloned/downloaded it, no configuration needed (overridable in
`config/policy.json`, see "Customize Workspace & Security" below)

**Protected Paths**: Windows, System32, AppData, etc. are write-blocked

## 📚 Documentation

- **[documents/QUICKSTART.md](documents/QUICKSTART.md)** — 30-second setup guide
- **[documents/RUN_CHECKLIST.md](documents/RUN_CHECKLIST.md)** — Step-by-step manual setup
- **[documents/OLLAMA_AUTO_SETUP.md](documents/OLLAMA_AUTO_SETUP.md)** — Automatic Ollama management
- **[documents/HALLUCINATION_FIXES.md](documents/HALLUCINATION_FIXES.md)** — How model accuracy was improved
- **[documents/FEATURE_SUMMARY.md](documents/FEATURE_SUMMARY.md)** — Complete feature overview
- **[documents/plan.md](documents/plan.md)** — Long-term vision and architecture
- **[CLAUDE.md](CLAUDE.md)** — Architecture guide for AI coding assistants working in this repo

## 📋 Project Structure

```
local_cli_agent/
├── CLIagent.py              # Entry point
├── config.py                # Configuration & system prompt
├── conversation.py          # Chat history management
├── ollama_client.py         # LLM interface
├── tool_executor.py         # Tool dispatcher
├── policy_engine.py         # Permission & safety checks
├── logger.py                # Structured activity logging
├── ollama_setup.py          # Automatic Ollama setup
│
├── tools/                   # Individual tool implementations
│   ├── read_file.py
│   ├── read_directory.py
│   ├── write_file.py
│   ├── search_files.py
│   ├── git_*.py            # Git commands
│   ├── python_runner.py
│   ├── pip_tools.py
│   ├── system_info.py
│   └── ... (43 tools)
│
├── config/                  # Configuration files
│   ├── models.json          # Model defaults & allowed list
│   └── policy.json          # Security policies
│
├── tests/                   # Test datasets
│   ├── cli_agent_evaluation_dataset.json
│   └── smoke_tests.py
│
└── logs/                    # Agent activity logs (JSON)
```

## ⚙️ Configuration

### Change Default Model

Edit `config/models.json`:

```json
{
  "default": "qwen2.5:1.5b",  // Faster, less accurate
  "allowed": [
    "qwen2.5:0.5b",
    "qwen2.5:1.5b",
    "qwen2.5:1.5b-instruct",
    "qwen2.5:3b"              // Default: larger, more accurate
  ]
}
```

### Customize Workspace & Security

By default the workspace boundary — the folder that write/dangerous tools are
restricted to — is the project's own directory, auto-detected from wherever you
cloned or downloaded it. No configuration needed: clone the repo, install
requirements, run `python CLIagent.py`, and the agent can read/write anywhere
inside that folder and nowhere else.

To point the agent at a *different* folder instead, edit `config/policy.json`:

```json
{
  "workspace_subpath": "Projects",           // Optional override — leave "" for the default
  "protected_path_names": [...],             // Never write to these
  "dangerous_patterns": [...],               // Block on substring match
  "max_file_read_bytes": 1048576,           // 1 MB limit
  "command_timeout_seconds": 30             // Kill commands after 30s
}
```

- Leave `workspace_subpath` empty (`""`) to keep the portable default (the project folder).
- A relative value (e.g. `"Projects"`) resolves under your home directory (`~/Projects`).
- An absolute value (e.g. `"C:\\Users\\you\\SomeFolder"`) is used exactly as given.

## 🚀 Features & Roadmap

**Completed:**
- ✅ Process & service management tools
- ✅ Network diagnostics (ping, DNS, ports)
- ✅ File editing (find/replace, insert, delete)
- ✅ Terminal execution & command output capture

**In Progress:**
- [ ] Performance profiling
- [ ] Plugin system for custom tools

**Future (Phase 3):**
- [ ] Voice input (speech-to-text)
- [ ] Voice output (text-to-speech)

## ⚡ Performance Notes

This runs entirely on your local hardware — there is no cloud fallback, so response
speed depends heavily on your machine:

- **CPU-only inference** (no GPU available to Ollama) can take anywhere from a few
  seconds to several minutes per response for the default `qwen2.5:3b` model, especially
  after a large tool result (e.g. a big directory listing) is fed back into context
- **Low free RAM** (observed below ~1.5GB free) can slow inference further or cause the
  Ollama server to become unresponsive/crash — the agent prints a warning on startup if
  this looks likely
- If responses feel too slow, switch to a smaller model in `config/models.json`
  (`qwen2.5:1.5b` or `qwen2.5:0.5b` are both already listed as allowed) — trades accuracy
  for speed
- Each turn has a generous 10-minute hard ceiling as a last-resort safety net against
  genuine hangs; it will not fire on normal slow-but-working responses

## 🐛 Known Limitations

- **Single-threaded CLI** — Cannot handle concurrent requests
- **No undo** — Deletions are permanent
- **Text-based only** — No GUI or web interface yet
- **Windows-first** — Protected-path checks and the Ctrl+X cancel shortcut are
  Windows-specific; the agent runs on Mac/Linux too (those code paths are guarded) but
  is primarily developed and tested on Windows
- **Qwen 2.5 model** — Best results with 3B version; 1.5B/0.5B are smaller and faster
  but less accurate

## 📝 Testing

### Smoke Tests

Validate the agent can answer standard questions (requires Ollama running):

```bash
python tests/smoke_tests.py
```

Results written to `logs/smoke_test_<timestamp>.log`. These tool-execution events are
tagged `"source": "smoke_test"` in the daily activity log so they're distinguishable
from real interactive sessions (which are tagged `"source": "interactive"`).

### Evaluation Dataset

50+ test cases covering filesystem, Git, Python, system info, security policies, error handling, and regression tests:

```bash
# View test cases
cat tests/cli_agent_evaluation_dataset.json
```

## 🔐 Security Notes

- **No raw shell access** — Only registered tools are available
- **Input validation** — All paths, commands, and queries are checked
- **Policy enforcement** — Dangerous operations require typed approval
- **Logging** — All activity is logged to `logs/agent_<DD_MM_YYYY>.txt` (one file per day) for audit
- **Offline operation** — Runs entirely locally; no cloud dependencies

## 📄 License

This project is provided as an open-source prototype.

## 🤝 Contributing

This is an initial prototype. Contributions, feedback, and feature requests are welcome! Please open an issue or pull request.

## 🙋 Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Docs**: See the documentation files for detailed guides

---

**Status**: Initial Prototype (v0.1)  
**Built with**: Python, Ollama, Qwen 2.5  
**Platform**: Windows-first, Mac/Linux code paths present but less tested  
**Last Updated**: August 13, 2026
