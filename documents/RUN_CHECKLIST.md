# 🚀 How to Run the Local CLI Agent

A step-by-step checklist to get the Local CLI Agent up and running from scratch.

---

## 0. ⚠️ Prerequisites (one-time setup)

Make sure these are installed before starting:

- [ ] **Python 3.8+** installed on your machine
- [ ] **Ollama** installed (download from https://ollama.com)
- [ ] **Git** (optional, only if pulling the repo)

---

## 1. ✅ Install Python dependencies

From the project folder, install the required Python package(s):

```cmd
cd "e:/My Projects/local_cli_agent"
pip install ollama
```

> **Verify:** `python --version` should print a Python 3.x version.

---

## 2. ✅ Run the CLI Agent (Automatic Setup)

The agent now **automatically**:
- Detects if Ollama server is running
- Starts Ollama server if not already running
- Pulls the default model if missing
- Then launches the interactive chat

Simply run:

```cmd
cd "e:/My Projects/local_cli_agent"
python CLIagent.py
```

On first run, you'll see a setup screen:

```
============================================================
🤖 Ollama Setup
============================================================

📍 Checking Ollama server...
✅ Ollama server is running

📍 Checking model: qwen2.5:3b
✅ Model 'qwen2.5:3b' is downloaded

✅ Ollama setup complete!
============================================================

🚀 Starting CLI Agent...

============================================================
Local CLI Agent
Model : qwen2.5:3b
Type 'exit' or 'quit' to stop.
============================================================
```

> **Note:** If you want to use a different model, edit `config/models.json` and change the `"default"` field before running.

> **Troubleshooting:** If Ollama is not installed, see `OLLAMA_AUTO_SETUP.md` for details.

---

## 5. ✅ Use the Agent

- Type a question at the `🙂 >` prompt and press **Enter**.
- The agent will call tools (execute shell commands) when needed and summarize the result.
- Type `exit` or `quit` to stop the agent.

---

## 6. ✅ (Optional) Run the Smoke Tests

To verify the agent can answer the standard test questions, and store results in `logs/`:

```cmd
cd "e:/My Projects/local_cli_agent"
python smoke_tests.py
```

A dated report is written to `logs/smoke_test_<timestamp>.log`.

---

## 🧠 Quick Reference

| Action                        | Command                            |
|-------------------------------|------------------------------------|
| **Run the agent (recommended)** | `python CLIagent.py`              |
| Run smoke tests                | `python smoke_tests.py`            |
| Stop the agent                 | type `exit` or `quit` at the prompt|
| Manual: Start Ollama server    | `ollama serve`                     |
| Manual: Pull a model           | `ollama pull qwen2.5:3b`           |
| Manual: List installed models  | `ollama list`                      |
| Install Python dependencies    | `pip install ollama psutil`        |

---

## 🛠️ Troubleshooting

| Problem                            | Fix                                                            |
|------------------------------------|----------------------------------------------------------------|
| `Ollama command not found`         | Install Ollama from https://ollama.com                        |
| `Ollama server startup timed out`  | Increase timeout in `ollama_setup.py` or start manually: `ollama serve` |
| `Model pull failed`                | Check internet connection, ensure 10+ GB disk space            |
| `ModuleNotFoundError: ollama`      | Run `pip install ollama psutil`.                             |
| Agent gives incorrect information  | The 3B model is more accurate; for best results ensure Ollama is fully running |

For detailed troubleshooting on automatic setup, see `OLLAMA_AUTO_SETUP.md`.
