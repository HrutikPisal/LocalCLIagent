import json

import ollama

from config import get_default_model, get_system_prompt
from logger import AgentLogger
from tool_executor import ToolExecutor
from tool_registry import TOOLS_SCHEMA


class OllamaClient:
    """Handles Ollama chat requests and tool-call loops."""

    def __init__(self, conversation):
        self.model = get_default_model()
        self.conversation = conversation
        self.executor = ToolExecutor()
        self.logger = AgentLogger()

        if not conversation.messages or conversation.messages[0].get("role") != "system":
            conversation.messages.insert(0, {"role": "system", "content": get_system_prompt(self.model)})

    def run(self) -> None:
        self._print_banner()

        while True:
            try:
                user_input = input("\n🙂 > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye.")
                break

            self.conversation.add_user(user_input)
            self.logger.log_prompt(user_input)

            try:
                reply = self._complete_turn()
                print(f"\n🤖 {reply}")
            except Exception as exc:
                print(f"\n❌ Error: {exc}")

    def _complete_turn(self) -> str:
        response = ollama.chat(
            model=self.model,
            messages=self.conversation.history(),
            tools=TOOLS_SCHEMA,
        )

        tools_used = []
        while response.get("message", {}).get("tool_calls"):
            assistant_message = response["message"]
            self.conversation.add_assistant_tool_calls(assistant_message)

            for tool_call in assistant_message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tools_used.append(tool_name)
                tool_output = self.executor.execute(tool_call)
                self.conversation.add_tool(tool_name, tool_output)

            response = ollama.chat(
                model=self.model,
                messages=self.conversation.history(),
                tools=TOOLS_SCHEMA,
            )

        final_content = response["message"].get("content", "").strip()
        self.conversation.add_assistant(final_content)
        self.logger.log_response(self.model, final_content, tools_used)
        return final_content or "(No response)"

    def _print_banner(self) -> None:
        print("=" * 60)
        print("Local CLI Agent")
        print(f"Model : {self.model}")
        print("Type 'exit' or 'quit' to stop.")
        print("=" * 60)
