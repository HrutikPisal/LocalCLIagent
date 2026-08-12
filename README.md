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
- **Python 3.8+** installed
- **Ollama** (download from [ollama.com](https://ollama.com))
- **Git** (optional, for version control)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/LocalCLIagent.git
cd LocalCLIagent

# Install Python dependencies
pip install ollama psutil

# Start the agent (automatic setup)
python CLIagent.py
```

The agent will automatically:
- ✅ Detect if Ollama server is running
- ✅ Start Ollama if needed (if installed)
- ✅ Pull the default model if missing
- ✅ Launch interactive chat

## 💬 Example Usage

```
🙂 > What Python version is installed?
🤖 The installed Python version is 3.11.3, located at C:\Program Files\Python311\python.exe.

🙂 > Show me the files in the current directory.
🤖 The current directory contains: README.md, src/ (folder), and requirements.txt.

🙂 > What's the status of my git repo?
🤖 On branch main: src/app.py is modified, and notes.txt is untracked.

🙂 > exit
Goodbye.
```

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

**Workspace**: Restricted to `~/Projects` by default (configurable in `config/policy.json`)

**Protected Paths**: Windows, System32, AppData, etc. are write-blocked

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** — 30-second setup guide
- **[RUN_CHECKLIST.md](RUN_CHECKLIST.md)** — Step-by-step manual setup
- **[OLLAMA_AUTO_SETUP.md](OLLAMA_AUTO_SETUP.md)** — Automatic Ollama management
- **[HALLUCINATION_FIXES.md](HALLUCINATION_FIXES.md)** — How model accuracy was improved
- **[FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)** — Complete feature overview
- **[plan.md](plan.md)** — Long-term vision and architecture

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

Edit `config/policy.json`:

```json
{
  "workspace_subpath": "Projects",           // Write boundary
  "protected_path_names": [...],             // Never write to these
  "dangerous_patterns": [...],               // Block on substring match
  "max_file_read_bytes": 1048576,           // 1 MB limit
  "command_timeout_seconds": 30             // Kill commands after 30s
}
```

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

## 🐛 Known Limitations

- **Single-threaded CLI** — Cannot handle concurrent requests
- **No undo** — Deletions are permanent
- **Text-based only** — No GUI or web interface yet
- **Windows-only** — Path handling is Windows-specific
- **Qwen 2.5 model** — Best results with 3B version; 1.5B smaller but less accurate

## 📝 Testing

### Smoke Tests

Validate the agent can answer standard questions:

```bash
python smoke_tests.py
```

Results written to `logs/smoke_test_<timestamp>.log`

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
- **Logging** — All activity is logged to `logs/agent.log` for audit
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
**Platform**: Windows  
**Last Updated**: August 2026
