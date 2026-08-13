import json
import platform
import threading
import time

import ollama

from config import get_default_model, get_system_prompt
from logger import AgentLogger
from tool_executor import ToolExecutor
from tool_registry import TOOLS_SCHEMA

# Ctrl+X cancel support (Windows only) via msvcrt raw keystroke reads.
#
# WHERE THIS WORKS:
#   - cmd.exe launched directly
#   - PowerShell (powershell.exe / pwsh.exe) launched directly, not through another
#     terminal emulator
#   - Windows Terminal, when it is the actual host process attached to the console
# These all provide a genuine Win32 console, which is what msvcrt.kbhit()/getch()
# read from directly.
#
# WHERE THIS DOES NOT RELIABLY WORK:
#   - VSCode's integrated terminal — it runs the shell behind ConPTY, a
#     pseudo-console layer that emulates a terminal over a pipe. ConPTY does not
#     guarantee raw control bytes (like Ctrl+X / 0x18) reach msvcrt the way a real
#     console does, so the keypress can silently fail to register.
#   - Git Bash / MinTTY / Cygwin — these never attach a real Win32 console at all,
#     so msvcrt calls on them are unreliable by design, not just under load.
#   - Any SSH or remote-desktop session relaying a terminal through a similar
#     pty/ConPTY bridge.
#
# Because of this, '.stop' (typed + Enter, read via the normal input() below) is
# kept as the mechanism guaranteed to work everywhere, and Ctrl+X is best-effort
# on top of it — if Ctrl+X doesn't register in your terminal, '.stop' still will.
if platform.system() == "Windows":
    try:
        import msvcrt
    except ImportError:
        msvcrt = None
else:
    msvcrt = None


class OllamaClient:
    """Handles Ollama chat requests and tool-call loops."""

    MAX_TOOL_CALLS_PER_TURN = 5
    CANCEL_KEYWORD = ".stop"

    # Hard ceiling on total turn wall-clock time, as a last-resort safety net against
    # genuine hangs (e.g. a wrong-tool retry loop, or Ollama becoming unresponsive).
    # Deliberately generous, not tuned for snappy UX: on this project's reference
    # hardware (CPU-only inference, qwen2.5:3b), a single non-tool-call response after
    # a large tool result has been observed taking up to ~9 minutes end-to-end. A short
    # timeout (e.g. 90-120s) would abort that legitimate case constantly. 600s (10 min)
    # is chosen as a ceiling that still lets normal slow-but-working turns finish, while
    # capping runaway multi-tool-call loops that would otherwise run unbounded.
    MAX_TURN_SECONDS = 600

    # Soft cap on generated tokens per model turn. This does not by itself prevent
    # context-window overflow (that's addressed by trimming large tool outputs before
    # they enter conversation history — see tools/read_directory.py, tools/search_files.py),
    # but it bounds worst-case generation time and avoids unbounded runaway output on this
    # RAM-constrained machine. num_ctx is intentionally left at the model's default rather
    # than being raised, since more context directly means more memory pressure on a
    # machine that has already been observed running under 1GB free RAM.
    NUM_PREDICT = 800

    def __init__(self, conversation):
        self.model = get_default_model()
        self.conversation = conversation
        self.executor = ToolExecutor()
        self.logger = AgentLogger()
        self.cancel_requested = False
        self.cancel_event = threading.Event()

        if not conversation.messages or conversation.messages[0].get("role") != "system":
            conversation.messages.insert(0, {"role": "system", "content": get_system_prompt(self.model)})

    def run(self) -> None:
        self._print_banner()
        self._print_help()

        while True:
            self.cancel_requested = False
            self.cancel_event.clear()
            try:
                user_input = input("\n[USER] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye.")
                break

            if user_input == self.CANCEL_KEYWORD:
                print("[AGENT] No active turn to cancel.")
                continue

            self.conversation.add_user(user_input)
            self.logger.log_prompt(user_input)

            print("[AGENT] Thinking... (this model can take a while on this machine; "
                  f"type '{self.CANCEL_KEYWORD}' anytime to cancel)", flush=True)

            self._start_cancel_listener()
            try:
                reply = self._complete_turn()
                if not self.cancel_requested:
                    print(f"\n[AGENT] {reply}")
                else:
                    print("\n[AGENT] (Turn cancelled.)")
            except Exception as exc:
                if self.cancel_requested:
                    print("\n[AGENT] (Turn cancelled.)")
                else:
                    print(f"\n[ERROR] Error: {exc}")
            finally:
                self.cancel_event.set()

    def _complete_turn(self) -> str:
        tools_used = []
        turn_deadline = time.monotonic() + self.MAX_TURN_SECONDS

        while True:
            if self.cancel_requested:
                return "(Turn cancelled.)"

            if time.monotonic() >= turn_deadline:
                timeout_message = (
                    f"(Stopped: this turn exceeded {self.MAX_TURN_SECONDS}s without "
                    "finishing. The model may be stuck retrying, or the machine may be "
                    "overloaded — try a simpler question, or check that Ollama is still "
                    "responsive.)"
                )
                self.conversation.add_assistant(timeout_message)
                self.logger.log_response(self.model, timeout_message, tools_used)
                return timeout_message

            message = self._stream_chat(turn_deadline)

            if self.cancel_requested:
                return "(Turn cancelled.)"

            if not message.get("tool_calls"):
                final_content = (message.get("content") or "").strip()
                if not final_content:
                    final_content = (
                        "(I wasn't able to generate a response for that. "
                        "This can happen when the model runs out of context on a large "
                        "tool result — try asking a more specific question, or ask again.)"
                    )
                self.conversation.add_assistant(final_content)
                self.logger.log_response(self.model, final_content, tools_used)
                return final_content

            if len(tools_used) >= self.MAX_TOOL_CALLS_PER_TURN:
                stop_message = "(Stopped: reached the maximum number of chained tool calls for this turn.)"
                self.conversation.add_assistant(stop_message)
                self.logger.log_response(self.model, stop_message, tools_used)
                return stop_message

            self.conversation.add_assistant_tool_calls({
                "role": "assistant",
                "content": message.get("content", ""),
                "tool_calls": message["tool_calls"],
            })

            for tool_call in message["tool_calls"]:
                if self.cancel_requested:
                    return "(Turn cancelled during tool execution.)"

                tool_name = tool_call["function"]["name"]
                tools_used.append(tool_name)
                tool_output = self.executor.execute(tool_call)
                self.conversation.add_tool(tool_name, tool_output)

            if self.cancel_requested:
                return "(Turn cancelled during tool execution.)"

    def _stream_chat(self, turn_deadline: float) -> dict:
        """Stream a chat response, checking cancel_requested and the turn
        deadline after every chunk so a turn can be interrupted mid-generation
        (including during a single, long, tool-free response) instead of only
        between tool-call rounds or after the full response completes."""
        stream = ollama.chat(
            model=self.model,
            messages=self.conversation.history(),
            tools=TOOLS_SCHEMA,
            stream=True,
            options={"num_predict": self.NUM_PREDICT},
        )

        content_parts = []
        tool_calls = None
        try:
            for chunk in stream:
                if self.cancel_requested or time.monotonic() >= turn_deadline:
                    break
                msg = chunk.get("message", {})
                if msg.get("content"):
                    content_parts.append(msg["content"])
                if msg.get("tool_calls"):
                    tool_calls = msg["tool_calls"]
        finally:
            close = getattr(stream, "close", None)
            if callable(close):
                close()

        result = {"content": "".join(content_parts)}
        if tool_calls:
            result["tool_calls"] = tool_calls
        return result

    def _start_cancel_listener(self) -> None:
        """Start the background thread that watches for a cancel signal while
        a turn is in progress. Uses the msvcrt-based listener (Ctrl+X + '.stop')
        when a real Windows console is available, otherwise falls back to a
        plain input()-based listener ('.stop' only) that works on every
        platform and terminal. See the module-level comment above the msvcrt
        import for exactly which terminals support Ctrl+X."""
        if msvcrt:
            target = self._listen_windows
        else:
            target = self._listen_fallback

        listener_thread = threading.Thread(target=target, daemon=True)
        listener_thread.start()

    def _listen_windows(self) -> None:
        """Raw keystroke listener for native Win32 consoles. Detects Ctrl+X
        (byte 0x18) instantly, and also buffers typed characters so '.stop'
        + Enter still works as a fallback in the same listener. Does NOT
        reliably see keystrokes under ConPTY-backed terminals (VSCode's
        integrated terminal) or Git Bash/MinTTY — see the module-level
        comment for details. If Ctrl+X silently does nothing in your
        terminal, type '.stop' + Enter instead."""
        input_buffer = ""
        while not self.cancel_event.is_set():
            try:
                if msvcrt.kbhit():
                    char = msvcrt.getch()

                    if char == b"\x18":  # Ctrl+X
                        self.cancel_requested = True
                        print("\n[AGENT] Cancelling turn (Ctrl+X)...", flush=True)
                        break

                    elif char in (b"\r", b"\n"):
                        if input_buffer.strip() == self.CANCEL_KEYWORD:
                            self.cancel_requested = True
                            print("\n[AGENT] Cancelling turn (.stop)...", flush=True)
                            break
                        input_buffer = ""

                    elif char == b"\x08":  # backspace
                        input_buffer = input_buffer[:-1]

                    elif 32 <= char[0] < 127:
                        input_buffer += chr(char[0])
                else:
                    self.cancel_event.wait(0.05)
            except Exception:
                break

    def _listen_fallback(self) -> None:
        """Plain input()-based listener for non-Windows platforms and for
        Windows environments without msvcrt. Only '.stop' + Enter is
        supported here — no raw keystroke detection, so no Ctrl+X."""
        while not self.cancel_event.is_set():
            try:
                user_input = input().strip()
                if user_input == self.CANCEL_KEYWORD:
                    self.cancel_requested = True
                    print("\n[AGENT] Cancelling turn (.stop)...", flush=True)
                    break
            except (EOFError, KeyboardInterrupt):
                break

    def _print_banner(self) -> None:
        print("=" * 60)
        print("Local CLI Agent")
        print(f"Model : {self.model}")
        print("Type 'exit' or 'quit' to stop.")
        print("=" * 60)

    def _print_help(self) -> None:
        print("\n[HELP] Controls:")
        if msvcrt:
            print(f"  - Press Ctrl+X OR type '{self.CANCEL_KEYWORD}' to cancel the current turn (works mid-generation)")
            print("    Ctrl+X needs a native console (cmd.exe/PowerShell/Windows Terminal run directly).")
            print("    It may not register in VSCode's integrated terminal or Git Bash — '.stop' always works.")
        else:
            print(f"  - Type '{self.CANCEL_KEYWORD}' anytime to cancel the current turn (works mid-generation)")
        print("  - Type 'exit' or 'quit' to close the agent")
        print("  - Press Ctrl+C to exit the agent immediately")
        print("=" * 60)
