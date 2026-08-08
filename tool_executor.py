import json
import time

from logger import AgentLogger
from policy_engine import PolicyDecision, PolicyEngine
from tool_registry import TOOL_MAP
from tools.path_utils import tool_result


class ToolExecutor:
    """Executes registered tools after policy checks."""

    def __init__(self):
        self.policy = PolicyEngine()
        self.logger = AgentLogger()

    def execute(self, tool_call: dict) -> str:
        tool_name = tool_call["function"]["name"]
        raw_args = tool_call["function"]["arguments"]

        arguments = self._parse_arguments(raw_args)

        if tool_name not in TOOL_MAP:
            return tool_result(False, error=f"Unknown tool: {tool_name}")

        entry = TOOL_MAP[tool_name]
        decision, reason = self.policy.evaluate(tool_name, arguments, entry)

        if decision == PolicyDecision.DENY:
            self.logger.log_policy_denial(tool_name, arguments, reason)
            return tool_result(False, error=f"Policy denied: {reason}")

        if decision == PolicyDecision.REQUIRE_APPROVAL:
            if not self._prompt_for_approval(tool_name, arguments, reason):
                self.logger.log_policy_denial(tool_name, arguments, "User denied approval.")
                return tool_result(False, error="User denied tool execution.")

        start = time.perf_counter()
        try:
            output = entry["function"](**arguments)
        except TypeError as exc:
            output = tool_result(False, error=f"Invalid tool arguments: {exc}")
        except Exception as exc:
            output = tool_result(False, error=str(exc))

        elapsed_ms = (time.perf_counter() - start) * 1000
        self.logger.log_tool(
            tool_name=tool_name,
            arguments=arguments,
            permission=entry.get("permission", "read"),
            output=output,
            execution_time_ms=elapsed_ms,
            decision=decision.value,
        )
        return output

    @staticmethod
    def _parse_arguments(raw_args) -> dict:
        if isinstance(raw_args, dict):
            return raw_args
        if isinstance(raw_args, str):
            try:
                parsed = json.loads(raw_args)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        return {}

    @staticmethod
    def _prompt_for_approval(tool_name: str, arguments: dict, reason: str) -> bool:
        print()
        print("=" * 60)
        print("APPROVAL REQUIRED")
        print(f"Tool      : {tool_name}")
        print(f"Reason    : {reason}")
        print(f"Arguments : {json.dumps(arguments, indent=2)}")
        print("=" * 60)
        answer = input("Allow this action? [y/N]: ").strip().lower()
        return answer in {"y", "yes"}
