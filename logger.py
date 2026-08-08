import json
from datetime import datetime
from pathlib import Path

from config import LOGS_DIR


class AgentLogger:
    """Writes structured agent activity to logs/agent.log."""

    def __init__(self, log_file: str = "agent.log"):
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.log_path = LOGS_DIR / log_file

    def _write(self, entry: dict) -> None:
        entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = json.dumps(entry, ensure_ascii=False)
        with open(self.log_path, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def log_prompt(self, prompt: str) -> None:
        self._write({"event": "user_prompt", "prompt": prompt})

    def log_tool(
        self,
        tool_name: str,
        arguments: dict,
        permission: str,
        output: str,
        execution_time_ms: float,
        decision: str = "allow",
    ) -> None:
        self._write(
            {
                "event": "tool_execution",
                "tool": tool_name,
                "arguments": arguments,
                "permission": permission,
                "decision": decision,
                "output_full": output,
                "output_length": len(output),
                "execution_time_ms": round(execution_time_ms, 2),
            }
        )

    def log_policy_denial(self, tool_name: str, arguments: dict, reason: str) -> None:
        self._write(
            {
                "event": "policy_denial",
                "tool": tool_name,
                "arguments": arguments,
                "reason": reason,
            }
        )

    def log_response(self, model: str, response: str, tools_used: list[str] | None = None) -> None:
        self._write(
            {
                "event": "assistant_response",
                "model": model,
                "response": response[:1000],
                "tools_used": tools_used or [],
                "response_length": len(response),
            }
        )
