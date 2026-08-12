from config import get_system_prompt

MAX_HISTORY_MESSAGES = 40  # excludes the system prompt


class Conversation:
    """Maintains chat history for the Ollama client."""

    def __init__(self, system_prompt: str | None = None):
        if system_prompt is None:
            system_prompt = get_system_prompt()
        self.messages = [{"role": "system", "content": system_prompt}]

    def _trim(self) -> None:
        if len(self.messages) > MAX_HISTORY_MESSAGES + 1:
            self.messages = [self.messages[0]] + self.messages[-MAX_HISTORY_MESSAGES:]

    def add_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})
        self._trim()

    def add_assistant(self, text: str) -> None:
        self.messages.append({"role": "assistant", "content": text})
        self._trim()

    def add_tool(self, name: str, output: str) -> None:
        self.messages.append({"role": "tool", "name": name, "content": output})
        self._trim()

    def add_assistant_tool_calls(self, message: dict) -> None:
        self.messages.append(message)
        self._trim()

    def history(self) -> list:
        return self.messages
