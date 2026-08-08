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

import ollama

from config import get_default_model


OLLAMA_API_URL = "http://localhost:11434/api/tags"
OLLAMA_TIMEOUT = 2


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
    print("🔄 Starting Ollama server...")

    try:
        if sys.platform == "win32":
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print("⏳ Waiting for Ollama server to start...")
        for i in range(15):
            time.sleep(1)
            if is_ollama_running():
                print("✅ Ollama server started successfully")
                return True
        print("⚠️  Ollama server startup timed out after 15 seconds")
        return False

    except FileNotFoundError:
        print("❌ Ollama command not found. Please install Ollama from https://ollama.com")
        return False
    except Exception as e:
        print(f"❌ Failed to start Ollama server: {e}")
        return False


def pull_model(model_name: str) -> bool:
    """Pull the specified model from Ollama."""
    print(f"📥 Pulling model: {model_name}")

    try:
        print(f"   This may take 1-5 minutes depending on internet speed...")
        ollama.pull(model_name)
        print(f"✅ Model '{model_name}' pulled successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to pull model '{model_name}': {e}")
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
    print("🤖 Ollama Setup")
    print("=" * 60)

    model_name = get_default_model()

    print(f"\n📍 Checking Ollama server...")
    if is_ollama_running():
        print("✅ Ollama server is running")
    else:
        print("❌ Ollama server not running")
        if not start_ollama_server():
            print("\n⚠️  Could not start Ollama server.")
            print("   Manual fix: Open a terminal and run: ollama serve")
            return False

    print(f"\n📍 Checking model: {model_name}")
    if model_exists(model_name):
        print(f"✅ Model '{model_name}' is downloaded")
    else:
        print(f"❌ Model '{model_name}' not found")
        if not pull_model(model_name):
            print("\n⚠️  Could not pull model.")
            print(f"   Manual fix: Run in terminal: ollama pull {model_name}")
            return False

    print("\n✅ Ollama setup complete!")
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
