import json
import threading
import sys
import platform

import ollama

from config import get_default_model, get_system_prompt
from logger import AgentLogger
from tool_executor import ToolExecutor
from tool_registry import TOOLS_SCHEMA

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
        if self.cancel_requested:
            return "(Turn cancelled before starting.)"

        response = ollama.chat(
            model=self.model,
            messages=self.conversation.history(),
            tools=TOOLS_SCHEMA,
        )

        tools_used = []
        while response.get("message", {}).get("tool_calls"):
            if self.cancel_requested:
                return "(Turn cancelled during tool execution.)"

            if len(tools_used) >= self.MAX_TOOL_CALLS_PER_TURN:
                stop_message = "(Stopped: reached the maximum number of chained tool calls for this turn.)"
                self.conversation.add_assistant(stop_message)
                self.logger.log_response(self.model, stop_message, tools_used)
                return stop_message

            assistant_message = response["message"]
            self.conversation.add_assistant_tool_calls(assistant_message)

            for tool_call in assistant_message["tool_calls"]:
                if self.cancel_requested:
                    return "(Turn cancelled during tool execution.)"

                tool_name = tool_call["function"]["name"]
                tools_used.append(tool_name)
                tool_output = self.executor.execute(tool_call)
                self.conversation.add_tool(tool_name, tool_output)

            if self.cancel_requested:
                return "(Turn cancelled during tool execution.)"

            response = ollama.chat(
                model=self.model,
                messages=self.conversation.history(),
                tools=TOOLS_SCHEMA,
            )

        final_content = response["message"].get("content", "").strip()
        self.conversation.add_assistant(final_content)
        self.logger.log_response(self.model, final_content, tools_used)
        return final_content or "(No response)"

    def _start_cancel_listener(self) -> None:
        def listen_for_cancel():
            if platform.system() == "Windows" and msvcrt:
                self._listen_windows()
            else:
                self._listen_posix()

        listener_thread = threading.Thread(target=listen_for_cancel, daemon=True)
        listener_thread.start()

    def _listen_windows(self) -> None:
        input_buffer = ""
        while not self.cancel_event.is_set():
            try:
                if msvcrt.kbhit():
                    char = msvcrt.getch()
                    if char == b'\x18':
                        self.cancel_requested = True
                        print("\n[AGENT] Cancelling turn (Ctrl+X)...")
                        break
                    elif char == b'\r':
                        if input_buffer.strip() == self.CANCEL_KEYWORD:
                            self.cancel_requested = True
                            print("\n[AGENT] Cancelling turn (.stop)...")
                            break
                        input_buffer = ""
                    elif char == b'\x08':
                        input_buffer = input_buffer[:-1]
                    elif 32 <= char[0] < 127:
                        input_buffer += chr(char[0])
                threading.Event().wait(0.01)
            except (EOFError, KeyboardInterrupt, Exception):
                break

    def _listen_posix(self) -> None:
        while not self.cancel_event.is_set():
            try:
                user_input = input().strip()
                if user_input == self.CANCEL_KEYWORD:
                    self.cancel_requested = True
                    print("\n[AGENT] Cancelling turn (.stop)...")
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
        cancel_help = "Press Ctrl+X OR type '.stop'" if (platform.system() == "Windows" and msvcrt) else f"Type '{self.CANCEL_KEYWORD}'"
        print(f"  - {cancel_help} to cancel the current turn")
        print("  - Type 'exit' or 'quit' to close the agent")
        print("  - Press Ctrl+C to exit the agent immediately")
        print("="  * 60)
