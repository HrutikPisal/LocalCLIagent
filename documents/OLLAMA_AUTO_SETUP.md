# Automatic Ollama Setup - Feature Guide

## Overview

The CLI Agent now **automatically handles Ollama server setup** when you run it. No more manual `ollama serve` or `ollama pull` commands needed!

Simply run:
```bash
python CLIagent.py
```

The agent will:
1. Check if Ollama server is running
2. Start it automatically if not (if Ollama is installed)
3. Check if the default model is downloaded
4. Pull it automatically if missing
5. Then launch the interactive chat

---

## Architecture

### New Module: `ollama_setup.py`

Provides utility functions for automatic Ollama lifecycle management:

| Function | Purpose |
|----------|---------|
| `is_ollama_running()` | Checks if Ollama server is responding on `localhost:11434` |
| `start_ollama_server()` | Attempts to start Ollama via `ollama serve` command |
| `pull_model(model_name)` | Downloads a model using `ollama.pull()` |
| `model_exists(model_name)` | Checks if a model is already downloaded |
| `setup_ollama()` | Full setup flow with user feedback |
| `ensure_ollama_ready()` | Entry point — checks + starts + pulls as needed |

### Updated `CLIagent.py`

Calls `ensure_ollama_ready()` before launching the agent:

```python
def main() -> None:
    if not ensure_ollama_ready():
        print("❌ Ollama setup failed...")
        return
    
    conversation = Conversation()
    agent = OllamaClient(conversation)
    agent.run()
```

---

## User Experience

### Scenario 1: Everything Already Set Up

```
$ python CLIagent.py

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

🙂 >
```

---

### Scenario 2: Ollama Not Running (Server Needs Start)

```
$ python CLIagent.py

============================================================
🤖 Ollama Setup
============================================================

📍 Checking Ollama server...
❌ Ollama server not running

🔄 Starting Ollama server...
⏳ Waiting for Ollama server to start...
✅ Ollama server started successfully

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

🙂 >
```

---

### Scenario 3: Model Not Downloaded (Needs Pull)

```
$ python CLIagent.py

============================================================
🤖 Ollama Setup
============================================================

📍 Checking Ollama server...
✅ Ollama server is running

📍 Checking model: qwen2.5:3b
❌ Model 'qwen2.5:3b' not found

📥 Pulling model: qwen2.5:3b
   This may take 1-5 minutes depending on internet speed...
✅ Model 'qwen2.5:3b' pulled successfully

✅ Ollama setup complete!
============================================================

🚀 Starting CLI Agent...

[... agent starts ...]
```

---

### Scenario 4: Ollama Not Installed (Graceful Error)

```
$ python CLIagent.py

============================================================
🤖 Ollama Setup
============================================================

📍 Checking Ollama server...
❌ Ollama server not running

🔄 Starting Ollama server...
❌ Ollama command not found. Please install Ollama from https://ollama.com

⚠️  Could not start Ollama server.
   Manual fix: Open a terminal and run: ollama serve

❌ Ollama setup failed. Please fix the issues above and try again.
   See RUN_CHECKLIST.md for manual setup instructions.
```

---

## How It Works (Technical Details)

### 1. Server Detection

```python
def is_ollama_running() -> bool:
    """Check if Ollama server is responding."""
    try:
        ollama.list()  # Try to list models
        return True
    except Exception:
        return False
```

Attempts to connect to Ollama's API. If successful, server is running.

---

### 2. Server Start

```python
def start_ollama_server() -> bool:
    """Attempt to start Ollama server."""
    subprocess.Popen(["ollama", "serve"], ...)
    
    for i in range(15):  # Wait up to 15 seconds
        time.sleep(1)
        if is_ollama_running():
            return True
    return False
```

Starts Ollama in the background and waits up to 15 seconds for it to respond.

---

### 3. Model Download

```python
def pull_model(model_name: str) -> bool:
    """Pull the specified model from Ollama."""
    ollama.pull(model_name)  # Uses ollama Python library
    return True
```

Uses the `ollama` library to download the default model. Can take 1-5 minutes depending on model size and internet speed.

---

### 4. Model Existence Check

```python
def model_exists(model_name: str) -> bool:
    """Check if a model is already downloaded."""
    models = ollama.list()
    for model in models.get("models", []):
        if model.get("name") == model_name or \
           model.get("name", "").startswith(model_name.split(":")[0]):
            return True
    return False
```

Queries Ollama's model list and checks if the desired model is present.

---

## Configuration

The setup automatically uses:
- **Default Model**: `qwen2.5:3b` (from `config/models.json`)
- **Ollama Server**: `http://localhost:11434` (default Ollama port)
- **Startup Timeout**: 15 seconds for Ollama to become responsive

To change the default model:
1. Edit `config/models.json`
2. Change `"default": "qwen2.5:3b"` to your preferred model
3. Next run of `CLIagent.py` will auto-pull the new default

---

## Troubleshooting

### "Ollama command not found"
**Cause**: Ollama is not installed or not in PATH.

**Fix**:
- Download Ollama from https://ollama.com
- Install and add to system PATH
- Restart terminal

### "Ollama server startup timed out"
**Cause**: Ollama is taking longer than 15 seconds to start (slow system, first run).

**Fix**:
- Increase startup timeout in `ollama_setup.py` line ~50 (change `range(15)` to `range(30)`)
- Or manually start: `ollama serve` in a terminal

### "Model pull failed"
**Cause**: Internet issue, disk space, or Ollama server problem.

**Fix**:
- Check internet connection
- Ensure 10+ GB free disk space (for 3B model)
- Try manual pull: `ollama pull qwen2.5:3b`

### "ModuleNotFoundError: ollama"
**Cause**: Python `ollama` library not installed.

**Fix**:
```bash
pip install ollama
```

---

## Backward Compatibility

- **Existing scripts**: `CLIagent.py` still works the same; setup just happens automatically now
- **Manual setup**: Users can still manually run `ollama serve` and `ollama pull` if they prefer
- **Logging**: Setup messages print to console but don't affect structured logs in `logs/agent.log`

---

## Benefits vs. Old Approach

| Aspect | Old | New |
|--------|-----|-----|
| **Setup Steps** | 2 (start Ollama, pull model) | 1 (run agent) |
| **Terminal Windows** | 2 (Ollama server + agent) | 1 (just agent) |
| **User Experience** | Manual, error-prone | Automated, guided |
| **Error Recovery** | User must debug | Clear error messages + fallback |
| **First-Time Setup** | Confusing | Friendly onboarding |

---

## Future Enhancements

Possible improvements (not yet implemented):
1. Auto-detect available RAM and suggest appropriate model size
2. Cached setup state to skip checks on subsequent runs
3. Background Ollama server management (restart if crashed)
4. Model auto-update checks
5. Multi-model support with automatic switching

---

## Files Modified

- **ollama_setup.py** (NEW) — Automatic Ollama lifecycle management
- **CLIagent.py** — Call `ensure_ollama_ready()` at startup

---

## Testing

To test the setup functionality:

```bash
# Test 1: Normal run (server running, model exists)
python CLIagent.py

# Test 2: Kill Ollama server, then run (should auto-restart)
# (Kill Ollama process in Task Manager or terminal)
python CLIagent.py

# Test 3: Delete the model, then run (should auto-pull)
# (Run: ollama rm qwen2.5:3b)
python CLIagent.py
```

All scenarios should succeed and launch the agent without manual intervention.
