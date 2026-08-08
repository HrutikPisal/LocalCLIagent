# Quick Start - Local CLI Agent

## ⚡ 30-Second Setup

### 1. **Install Ollama** (one-time)
Download from https://ollama.com and install.

### 2. **Install Python packages** (one-time)
```bash
cd "e:/My Projects/local_cli_agent"
pip install ollama psutil
```

### 3. **Run the agent**
```bash
python CLIagent.py
```

That's it! The agent automatically:
- Starts Ollama server if needed
- Downloads the model if missing
- Launches interactive chat

---

## 💬 Use the Agent

```
🙂 > Hello

🤖 Hi! How can I help?

🙂 > What Python version is installed?

🤖 The Python version installed on this system is 3.11.3...

🙂 > Show current directory

🤖 Here are the files in the current directory...

🙂 > exit
```

Type `exit` or `quit` to stop.

---

## 📝 Common Tasks

| Task | Command |
|------|---------|
| See Python version | `python --version` |
| List installed packages | `pip list` |
| Pull a different model | `ollama pull qwen2.5:1.5b` |
| Use a different model | Edit `config/models.json` and change default |
| View logs | `cat logs/agent.log` |
| Run tests | `python smoke_tests.py` |

---

## ❓ Problems?

| Issue | Fix |
|-------|-----|
| "Ollama not found" | Install from https://ollama.com |
| "ModuleNotFoundError: ollama" | `pip install ollama` |
| Agent gives wrong answers | Normal for small models; larger models are more accurate |
| Slow response | 3B model is slower than 1.5B; use `qwen2.5:1.5b` if speed matters |

---

## 📚 Full Documentation

- `RUN_CHECKLIST.md` — Step-by-step setup
- `OLLAMA_AUTO_SETUP.md` — How automatic setup works
- `HALLUCINATION_FIXES.md` — Why answers are more accurate
- `FEATURE_SUMMARY.md` — What changed
- `plan.md` — Project vision and architecture

---

## 🚀 You're Ready!

```bash
python CLIagent.py
```

Enjoy your local AI assistant! 🤖
