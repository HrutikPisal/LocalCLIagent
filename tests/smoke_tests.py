"""
smoke_tests.py
==============

Automated smoke test suite for the Local CLI Agent.

Validates that the agent can answer standard questions using registered tools.
Results are written to logs/smoke_test_<timestamp>.log
"""

import datetime
import json
import sys

import ollama

from config import get_default_model, get_system_prompt
from tool_executor import ToolExecutor
from tool_registry import TOOLS_SCHEMA


MODEL = get_default_model()
EXECUTOR = ToolExecutor()


TESTS = [
    {
        "name": "What model are you?",
        "question": "What model are you?",
        "expect_response_contains": ["qwen", "Qwen"],
        "expect_tools": None,
    },
    {
        "name": "What operating system am I using?",
        "question": "What operating system am I using?",
        "expect_response_contains": ["Windows", "windows", "Linux", "linux", "Darwin"],
        "expect_tools": ["system_info"],
    },
    {
        "name": "Show current directory",
        "question": "Show current directory",
        "expect_response_contains": None,
        "expect_tools": ["system_info", "read_directory"],
    },
    {
        "name": "List files here",
        "question": "List files here",
        "expect_response_contains": None,
        "expect_tools": ["read_directory"],
    },
    {
        "name": "What Python version is installed?",
        "question": "What Python version is installed?",
        "expect_response_contains": ["3."],
        "expect_tools": ["system_info", "run_python"],
    },
    {
        "name": "Plain greeting should not call tools",
        "question": "Hello",
        "expect_response_contains": None,
        "expect_tools": [],
    },
    {
        "name": "Small talk should not call tools",
        "question": "Thanks, that's helpful!",
        "expect_response_contains": None,
        "expect_tools": [],
    },
]


def run_smoke_tests():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"logs/smoke_test_{timestamp}.log"

    results = []
    lines = [
        "=" * 70,
        "LOCAL CLI AGENT - SMOKE TEST REPORT",
        f"Timestamp : {timestamp}",
        f"Model     : {MODEL}",
        "=" * 70,
        "",
    ]

    for test in TESTS:
        lines.append("-" * 70)
        lines.append(f"TEST: {test['name']}")
        lines.append(f"QUESTION: {test['question']}")
        lines.append("")

        messages = [
            {"role": "system", "content": get_system_prompt(MODEL)},
            {"role": "user", "content": test["question"]},
        ]

        tool_calls = []
        final_response = ""
        passed = True
        fail_reason = ""

        try:
            response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS_SCHEMA)

            while response.get("message", {}).get("tool_calls"):
                assistant_message = response["message"]
                messages.append(assistant_message)

                for tool_call in assistant_message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_calls.append(tool_name)
                    tool_output = EXECUTOR.execute(tool_call)
                    messages.append(
                        {"role": "tool", "name": tool_name, "content": tool_output}
                    )

                response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS_SCHEMA)

            final_response = response["message"].get("content", "")

        except Exception as exc:
            passed = False
            fail_reason = f"Exception: {exc}"

        if tool_calls:
            lines.append("TOOL CALLS:")
            for name in tool_calls:
                lines.append(f"  - {name}")
        else:
            lines.append("TOOL CALLS: (none)")

        lines.append("")
        lines.append(f"FINAL RESPONSE: {final_response}")
        lines.append("")

        if passed and test["expect_response_contains"]:
            if not any(kw.lower() in final_response.lower() for kw in test["expect_response_contains"]):
                passed = False
                fail_reason = f"Response missing keywords: {test['expect_response_contains']}"

        if passed and test["expect_tools"] == []:
            if tool_calls:
                passed = False
                fail_reason = f"Expected no tool calls, got {tool_calls}"

        if passed and test["expect_tools"]:
            if not tool_calls:
                passed = False
                fail_reason = "Expected tool calls but none were made."
            elif not any(name in test["expect_tools"] for name in tool_calls):
                passed = False
                fail_reason = f"Expected one of {test['expect_tools']}, got {tool_calls}"

        status = "PASS" if passed else "FAIL"
        results.append((test["name"], status))

        lines.append(f"RESULT: {status}")
        if not passed:
            lines.append(f"REASON: {fail_reason}")
        lines.append("-" * 70)
        lines.append("")
        print(f"[{status}] {test['name']}")

    passes = sum(1 for _, status in results if status == "PASS")
    fails = len(results) - passes

    lines.extend(
        [
            "=" * 70,
            "SUMMARY",
            f"  Total tests : {len(results)}",
            f"  Passed      : {passes}",
            f"  Failed      : {fails}",
            "",
        ]
    )
    for name, status in results:
        lines.append(f"  {status}: {name}")
    lines.append("")
    lines.append("=" * 70)

    with open(log_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))

    print()
    print(f"Smoke test report written to: {log_path}")
    print(f"Summary: {passes} passed, {fails} failed")
    return passes, fails


if __name__ == "__main__":
    passed, failed = run_smoke_tests()
    sys.exit(1 if failed > 0 else 0)
