# Cross-Platform Python CLI Development Plan: Text & Voice Architecture

This document outlines a robust, three-phase engineering blueprint for building a cross-platform Command Line Interface (CLI) application in Python. The project evolves from a Windows-based text retrieval tool into a multi-modal (text and voice), OS-agnostic application.

---

## Phase 1: Core Text Fetching Engine (Windows)

The objective of this phase is to establish the backbone of the application: the data fetching logic and the terminal interface. By isolating the text-based interactions first, you ensure the core logic is stable before introducing hardware-dependent audio drivers.

### 1. The CLI Framework
*   **Recommendation:** Use **Typer** (built on top of Click).
*   **Why:** Typer leverages Python type hints to automatically generate CLI arguments, options, and help texts. It is exceptionally clean and reduces boilerplate.
*   **Execution:** Create a main entry point (e.g., `main.py`) that handles command routing without touching the actual data logic.

### 2. The Fetching Engine (NLP & RAG Integration)
Since the primary function is "text-based fetching," this module should be designed to handle advanced text retrieval.
*   **Architecture:** Decouple the query processing from the CLI output. Create a dedicated `retrieval` module.
*   **Implementation:** If the CLI is retrieving complex domain-specific information (such as querying a legal database or document store), design this module to support a **Retrieval-Augmented Generation (RAG)** pipeline. This allows the CLI to process natural language queries, fetch relevant context from a local vector store or database, and return highly accurate text.
*   **Libraries:** Consider incorporating `Hugging Face` transformers or `LangChain` if the text fetching requires semantic search rather than just keyword matching.

### 3. File & Path Management
*   **Strict Rule:** Use Python's built-in `pathlib` for all file operations.
*   **Why:** Even though Phase 1 is Windows-only, using `Path("data") / "config.json"` ensures that when you transition to Linux/macOS in Phase 3, you will not face directory traversal crashes caused by hardcoded backslashes (`\`).

---

## Phase 2: Dual Mode (Text & Voice) on Windows

With the text fetching engine working perfectly, Phase 2 introduces multi-modal interaction. Windows provides built-in audio sub-systems that make this phase highly accessible without complex driver configurations.

### 1. Text-to-Speech (Output)
*   **Library:** `pyttsx3`
*   **Backend:** On Windows, `pyttsx3` automatically hooks into **SAPI5** (Microsoft Speech API).
*   **Advantages:** It processes speech entirely offline, ensuring low latency and data privacy for the fetched text.

### 2. Speech-to-Text (Input)
*   **Libraries:** `SpeechRecognition` combined with `PyAudio`.
*   **Microphone Access:** `PyAudio` connects directly to the Windows default recording device.
*   **Recognition Engine:** 
    *   Use `SpeechRecognition`'s `recognize_google()` for fast prototyping (requires an internet connection).
    *   For a fully offline, robust pipeline (especially if pairing with local RAG/NLP models), integrate the **Vosk** API. It runs locally and handles technical vocabularies well.

### 3. Mode Switching Architecture
*   Implement a global state or configuration flag in your Typer CLI.
*   Example CLI usage: 
    *   `mycli query "What is the status of the server?"` (Defaults to text I/O)
    *   `mycli listen --voice` (Activates the PyAudio stream, processes the spoken query, and reads the fetched results aloud via pyttsx3).

---

## Phase 3: Cross-Platform Transition (Windows, macOS, Linux)

Phase 3 transforms the Windows-bound CLI into a universal application. Python handles OS abstraction well, but hardware-level audio processing requires careful dependency management.

### 1. Abstracting Audio Dependencies
Audio drivers vary drastically across operating systems. Your code must detect the OS and handle missing dependencies gracefully.

| OS | Text-to-Speech (`pyttsx3`) | Speech-to-Text (`PyAudio`) |
| :--- | :--- | :--- |
| **Windows** | SAPI5 (Built-in) | Built-in |
| **macOS** | NSSpeechSynthesizer (Built-in) | Requires `portaudio` (`brew install portaudio`) |
| **Linux** | Requires `espeak-ng` & `libespeak1` | Requires `portaudio19-dev` (`apt-get install`) |

*   **Implementation:** Add a startup check using Python's `platform.system()`. If the user is on Linux and `espeak` is missing, the CLI should catch the exception and print a helpful error message instructing them to install the required system packages, rather than simply crashing.

### 2. Standardizing User Directories
*   **Library:** Use `platformdirs`.
*   **Why:** You cannot rely on Windows `%APPDATA%` for storing local configuration files, downloaded NLP models, or database caches. `platformdirs.user_data_dir("MyCLI")` automatically resolves to:
    *   `C:\Users\User\AppData\Local\MyCLI` on Windows
    *   `~/.local/share/MyCLI` on Linux
    *   `~/Library/Application Support/MyCLI` on macOS

### 3. Packaging and Distribution
To distribute the CLI without requiring users to manage Python environments and pip installs:
*   **Tool:** Use **PyInstaller**.
*   **Process:** You must run PyInstaller on the target operating system to generate the specific executable (run it on Windows for `.exe`, on macOS for the macOS binary, and on Linux for the ELF binary).
*   **Hidden Imports:** Audio libraries and NLP transformers often load dependencies dynamically. You will need to carefully configure your PyInstaller `.spec` file to include "hidden imports" so that drivers like SAPI5 or eSpeak are bundled correctly into the final executable.
