# Model Hallucination Fixes - Implementation Summary

## Problem Statement

The CLI agent was hallucinating factually incorrect information:
- **Windows version**: Said "Windows 10" when system is Windows 11 (build 26200)
- **CPU vendor**: Claimed "AMD Ryzen 5" when system has Intel Core
- **Directory contents**: Fabricated completely different file listings
- **Model identity**: Claimed to use "NeMo" framework when running Qwen 2.5 via Ollama
- **RAM usage**: Off by ~10 percentage points even though tool had correct total

Root cause: `qwen2.5:1.5b-instruct` (1.5B parameters) is too small to reliably ground itself to tool outputs; it falls back to parametric training-data hallucinations instead of faithfully transcribing JSON results.

---

## Implemented Fixes

### 1. ✅ Fixed `tools/system_info.py` — Windows Version Detection

**Problem**: `platform.release()` returns "10" for both Windows 10 and 11, making it unreliable.

**Solution**: Use `sys.getwindowsversion().build >= 22000` to definitively detect Windows 11.

**Change**:
- Added `_get_windows_version()` helper function
- Correctly detects Windows 11 when build >= 22000
- Renamed field from `os_release` to `os_name` for clarity
- Now returns "Windows 11" on the test system (which has build 26200)

```python
def _get_windows_version() -> str:
    """Detect Windows version correctly based on build number."""
    wv = sys.getwindowsversion()
    if wv.major == 10 and wv.minor == 0 and wv.build >= 22000:
        return "Windows 11"
    # ... fallback cases ...
```

**Test**: The tool will now correctly output `"os_name": "Windows 11"` even if the model tries to hallucinate.

---

### 2. ✅ Injected Real Model Identity into System Prompt

**Problem**: Prompt never told the model its actual identifier, so "What model are you?" fell back to training-data hallucination (claiming "NeMo", wrong framework).

**Solution**: Dynamically inject the real model name from config into the system prompt.

**Changes**:
- **config.py**: Converted static `SYSTEM_PROMPT` string to `get_system_prompt(model_name)` function
- **conversation.py**: Accept optional `system_prompt` parameter; call `get_system_prompt()` if not provided
- **ollama_client.py**: Ensure system prompt contains the actual model name before starting chat

**System Prompt now includes**:
```
Your model identifier is: {model_name}
```

When the model is asked "what model are you?", it can now ground the answer in the injected identifier rather than hallucinating from training data.

---

### 3. ✅ Strengthened Grounding Rules in System Prompt

**Problem**: Prompt said "never invent command outputs" but had no explicit rule against inventing hardware details, file sizes, percentages, or "plausible-sounding" data not in tool results.

**Solution**: Added explicit CRITICAL GROUNDING RULES section to prompt.

**New prompt rules**:
```
CRITICAL GROUNDING RULES:
- Only state values that appear literally in a tool's JSON output.
- Never invent file names, sizes, hardware details, or statistics.
- When a tool returns data, quote it verbatim or summarize only what it contains.
- If a tool returns unexpected data, acknowledge the tool result rather than inventing alternatives.
- Do not use parametric knowledge to "correct" or supplement tool outputs.
```

This explicitly forbids the types of hallucinations observed (AMD Ryzen claim, file size fabrication, directory listing invention).

---

### 4. ✅ Full Raw-Output Logging for Grounding Verification

**Problem**: Previous logs only stored 500-char `output_preview`; if a model hallucinated, we couldn't diff the raw tool JSON against the response to prove it was an invention.

**Solution**: Log the full tool output (not truncated).

**Changes in logger.py**:
- Replaced `output_preview: output[:500]` with `output_full: output`
- Added `output_length: len(output)` to track size
- Full JSON is now available for every tool execution

**Benefit**: Future mismatches like "agent said AMD Ryzen but tool returned Intel" can now be proven by diffing raw logs against chat transcripts.

---

### 5. ✅ (Optional) Upgraded Default Model

**Problem**: `qwen2.5:1.5b-instruct` is a lightweight model that struggles to ground itself to multi-field tool outputs; every test showed hallucinations on complex tools like `system_info`.

**Solution**: Changed default model from `qwen2.5:1.5b-instruct` to `qwen2.5:3b`.

**Change in config/models.json**:
```json
{
  "default": "qwen2.5:3b",
  "allowed": [
    "qwen2.5:0.5b",
    "qwen2.5:1.5b",
    "qwen2.5:1.5b-instruct",
    "qwen2.5:3b"
  ]
}
```

**Rationale**:
- 3B model is ~2x larger, better at following exact instructions and grounding to data
- Still fits in ~4-6GB RAM (user has 7.75GB available)
- Users can still downgrade to 1.5b if latency/memory is critical
- Requires: `ollama pull qwen2.5:3b` (one-time)

---

## Testing the Fixes

### Immediate Tests (no Ollama needed):
```bash
# Verify Windows version detection
python -c "from tools.system_info import system_info; import json; print(json.dumps(json.loads(system_info()), indent=2))" 

# Should show:
# "os_name": "Windows 11"  (not "Windows 10")
```

### Full Integration Test (requires Ollama server + model):
1. **Pull the new model**:
   ```bash
   ollama pull qwen2.5:3b
   ```

2. **Run the agent**:
   ```bash
   python CLIagent.py
   ```

3. **Test queries** (comparing to `actual_manual_terminal_response`):
   - `What model are you?` → Should mention `qwen2.5:3b` from injected prompt, not hallucinate framework
   - `What Windows version am I running?` → Should say "Windows 11" (tool now returns this correctly)
   - `Show current directory` → Should list actual files in the project, not fabricated home-directory contents
   - `What Python version is installed?` → Should correctly report 3.11.3
   - `What CPU do I have?` → Should say Intel, not AMD (if tool works correctly)

4. **Check logs** (`logs/agent.log`):
   - Look for `assistant_response` events with `"model": "qwen2.5:3b"`
   - Look for `tool_execution` events with full `output_full` JSON (no longer truncated)
   - Verify no discrepancies between tool JSON and what the response claims

---

## Files Modified

| File | Changes |
|------|---------|
| `tools/system_info.py` | Added Windows version detection by build number; renamed field to `os_name` |
| `config.py` | Converted static `SYSTEM_PROMPT` to `get_system_prompt(model_name)` function with grounding rules |
| `conversation.py` | Accept optional `system_prompt` parameter at init |
| `ollama_client.py` | Inject model name into system prompt before chat loop |
| `logger.py` | Log full tool output (`output_full`) instead of 500-char preview |
| `config/models.json` | Changed default from `qwen2.5:1.5b-instruct` to `qwen2.5:3b` |

---

## Backward Compatibility

- **Config.py**: Old static `SYSTEM_PROMPT` var still exists for backwards compat, but new code uses `get_system_prompt()`
- **Logging**: Full output is now logged instead of preview; existing logs are unaffected; future queries will have complete data
- **Models.json**: Users can still select `qwen2.5:1.5b-instruct` via config; default just changed

---

## Expected Improvements

| Issue | Before | After |
|-------|--------|-------|
| Windows version detection | Unreliable (platform.release()) | Reliable (build number check) |
| Self-identification | Hallucinates (claims NeMo) | Grounded (injected model name) |
| Hardware details | Fabricates (AMD when Intel) | Tool-driven (system_info returns actual) |
| Multi-field tool grounding | 1.5B model loses context | 3B model better context retention |
| Log auditability | 500-char preview | Full JSON available |
| Explicit grounding instruction | Generic "don't invent" | Specific "only literal JSON values" |

---

## Next Steps (Optional)

If issues persist:
1. Run smoke tests with new model: `python smoke_tests.py`
2. Review logs for any remaining hallucinations: `grep assistant_response logs/agent.log | jq`
3. If needed, consider even larger model (`mistral:7b`) or prompt engineering iteration
