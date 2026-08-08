from config import get_system_prompt


class Conversation:
    """Maintains chat history for the Ollama client."""

    def __init__(self, system_prompt: str | None = None):
        if system_prompt is None:
            system_prompt = get_system_prompt()
        self.messages = [{"role": "system", "content": system_prompt}]

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})

    def add_assistant(self, text: str) -> None:
        self.messages.append({"role": "assistant", "content": text})

    def add_tool(self, name: str, output: str) -> None:
        self.messages.append({"role": "tool", "name": name, "content": output})

    def add_assistant_tool_calls(self, message: dict) -> None:
        self.messages.append(message)

    def history(self) -> list:
        return self.messages
