# Logging Improvements - Updated Functionality

## What Changed

The `logs/agent.log` now captures **complete conversation turns** with model name, tools used, and final output.

---

## Before (Previous Logging)

Each turn produced minimal structured logs:

```json
{"event": "user_prompt", "prompt": "Show current directory", "timestamp": "2026-08-08 10:15:30"}
{"event": "tool_execution", "tool": "read_directory", "arguments": {}, "permission": "read", "decision": "allow", "output_preview": "{...}", "execution_time_ms": 45.2, "timestamp": "2026-08-08 10:15:30"}
```

**Missing:**
- Model name (which model generated the response?)
- Final LLM output (what did the agent say?)
- Which tools were called in the turn (had to parse tool_execution events)

---

## After (Updated Logging)

Now each turn produces a **complete conversation trace**:

```json
{"event": "user_prompt", "prompt": "Show current directory", "timestamp": "2026-08-08 10:15:30"}
{"event": "tool_execution", "tool": "read_directory", "arguments": {}, "permission": "read", "decision": "allow", "output_preview": "{...}", "execution_time_ms": 45.2, "timestamp": "2026-08-08 10:15:30"}
{"event": "assistant_response", "model": "qwen2.5:1.5b-instruct", "response": "Here is the current directory...", "tools_used": ["read_directory"], "response_length": 256, "timestamp": "2026-08-08 10:15:31"}
```

---

## New Fields in `assistant_response` Event

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | Name of the model that generated the response (e.g., `qwen2.5:1.5b-instruct`) |
| `response` | string | First 1000 characters of the assistant's response |
| `tools_used` | list[string] | Array of tool names called during this turn (empty if no tools) |
| `response_length` | integer | Total length of the full response (helps identify truncated responses) |
| `timestamp` | string | ISO timestamp of when the response was logged |

---

## Example Log Sequence (Multi-tool Turn)

A user asks "What Python version is installed and show me the project files?"

```json
{"event": "user_prompt", "prompt": "What Python version is installed and show me the project files?", "timestamp": "2026-08-08 10:20:45"}
{"event": "tool_execution", "tool": "system_info", "arguments": {}, "permission": "read", "decision": "allow", "output_preview": "{\"success\": true, \"os\": \"Windows 11\"...", "execution_time_ms": 23.1, "timestamp": "2026-08-08 10:20:45"}
{"event": "tool_execution", "tool": "read_directory", "arguments": {"directory": "."}, "permission": "read", "decision": "allow", "output_preview": "{\"success\": true, \"contents\": [...]}", "execution_time_ms": 12.5, "timestamp": "2026-08-08 10:20:46"}
{"event": "assistant_response", "model": "qwen2.5:1.5b-instruct", "response": "Python version 3.11.3 is installed at C:\\Program Files\\Python311\\python.exe. The project contains the following files: CLIagent.py, config.py, tool_registry.py...", "tools_used": ["system_info", "read_directory"], "response_length": 487, "timestamp": "2026-08-08 10:20:47"}
```

---

## How to Query Logs

### 1. View all assistant responses with models used:
```bash
grep "assistant_response" logs/agent.log | jq '.model, .tools_used'
```

### 2. Find which tools were used most:
```bash
grep "tool_execution" logs/agent.log | jq -r '.tool' | sort | uniq -c | sort -rn
```

### 3. See complete conversation turns:
```bash
grep -E "user_prompt|assistant_response" logs/agent.log | jq '{event, timestamp, model, prompt, tools_used}'
```

### 4. Check response times:
```bash
grep "assistant_response" logs/agent.log | jq '.response_length' | awk '{sum+=$1} END {print "Avg response length:", sum/NR}'
```

---

## Files Modified

- `logger.py`: Added `log_response()` method to log assistant responses with model name and tools used
- `ollama_client.py`: Track tools used during turn, call `log_response()` with model and tools list

---

## Backward Compatibility

All existing log entries remain unchanged. The new `assistant_response` event is an **addition**, not a replacement, so existing log parsing scripts continue to work.
