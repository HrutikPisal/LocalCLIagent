"""
Automatic Ollama setup and model management.

Handles:
- Detecting if Ollama server is running
- Starting Ollama server if available and not running
- Pulling the default model if missing
- Graceful error handling with user guidance
"""

import subprocess
import time
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

try:
    import psutil
except ImportError:
    psutil = None

import ollama

from config import get_default_model


OLLAMA_API_URL = "http://localhost:11434/api/tags"
OLLAMA_TIMEOUT = 2

# Threshold below which we warn before starting. Chosen from observed session logs
# where available RAM dropped to ~0.79-0.95GB free on a 7.75GB machine while running
# qwen2.5:3b (CPU-only inference); that same session ended with the Ollama server
# process crashing entirely mid-request. Not a hard block — the user may still proceed.
LOW_RAM_WARNING_GB = 1.5


def check_available_ram() -> None:
    """Warn if available RAM is low enough to risk the slowdowns/crashes observed
    in production logs. Best-effort: silently skips if psutil is unavailable."""
    if psutil is None:
        return
    try:
        available_gb = psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        return
    if available_gb < LOW_RAM_WARNING_GB:
        print(f"[WARN] Only {available_gb:.2f} GB RAM available. Local model inference "
              "can become very slow or the Ollama server can crash under this little "
              "headroom. Consider closing other applications before continuing.")


def is_ollama_running() -> bool:
    """Check if Ollama server is responding."""
    if requests is None:
        try:
            ollama.list()
            return True
        except Exception:
            return False

    try:
        response = requests.get(OLLAMA_API_URL, timeout=OLLAMA_TIMEOUT)
        return response.status_code == 200
    except Exception:
        return False


def start_ollama_server() -> bool:
    """Attempt to start Ollama server."""
    print("[...] Starting Ollama server...")

    try:
        if sys.platform == "win32":
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("[WAIT] Waiting for Ollama server to start...")
        for i in range(15):
            time.sleep(1)
            if is_ollama_running():
                print("[OK] Ollama server started successfully")
                return True
        print("[WARN] Ollama server startup timed out after 15 seconds")
        return False

    except FileNotFoundError:
        print("[ERROR] Ollama command not found. Please install Ollama from https://ollama.com")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to start Ollama server: {e}")
        return False


def pull_model(model_name: str) -> bool:
    """Pull the specified model from Ollama."""
    print(f"[PULL] Pulling model: {model_name}")

    try:
        print(f"   This may take 1-5 minutes depending on internet speed...")
        ollama.pull(model_name)
        print(f"[OK] Model '{model_name}' pulled successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to pull model '{model_name}': {e}")
        return False


def model_exists(model_name: str) -> bool:
    """Check if a model is already downloaded."""
    try:
        models = ollama.list()
        for model in models.get("models", []):
            if model.get("name") == model_name or model.get("name", "").startswith(model_name.split(":")[0]):
                return True
        return False
    except Exception:
        return False


def setup_ollama() -> bool:
    """
    Run full Ollama setup: start server if needed, pull default model if missing.

    Returns True if setup succeeded, False if setup failed and user should handle manually.
    """
    print("=" * 60)
    print("[BOT] Ollama Setup")
    print("=" * 60)

    check_available_ram()

    model_name = get_default_model()

    print(f"\n[CHECK] Checking Ollama server...")
    if is_ollama_running():
        print("[OK] Ollama server is running")
    else:
        print("[ERROR] Ollama server not running")
        if not start_ollama_server():
            print("\n[WARN]  Could not start Ollama server.")
            print("   Manual fix: Open a terminal and run: ollama serve")
            return False

    print(f"\n[CHECK] Checking model: {model_name}")
    if model_exists(model_name):
        print(f"[OK] Model '{model_name}' is downloaded")
    else:
        print(f"[ERROR] Model '{model_name}' not found")
        if not pull_model(model_name):
            print("\n[WARN]  Could not pull model.")
            print(f"   Manual fix: Run in terminal: ollama pull {model_name}")
            return False

    print("\n[OK] Ollama setup complete!")
    print("=" * 60)
    return True


def ensure_ollama_ready() -> bool:
    """
    Ensure Ollama is ready to use. Runs full setup if needed.
    Returns True if ready, False if manual intervention required.
    """
    if is_ollama_running() and model_exists(get_default_model()):
        return True

    return setup_ollama()
