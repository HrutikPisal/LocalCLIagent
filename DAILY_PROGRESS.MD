# Daily Progress

## 2026-08-14

### Completed
- QA'd today's interactive log (`logs/agent_14_08_2026.txt`) and found a regression:
  the "don't call tools for greetings" system-prompt guidance added on 2026-08-13 did
  not hold — a bare "Hello" still triggered a `system_info` call (~7.5 min round trip).
  Strengthened `config.py`'s system prompt with a concrete counter-example.
- Found and fixed a correctness bug: "What is your model?" was answered with OS/CPU/RAM
  specs (via a wrongly-called `system_info`) and never actually stated the model name,
  even though the model identifier is already injected into the system prompt. Added
  explicit guidance to answer identity questions directly, no tool call.
- Found and fixed a gap in the 2026-08-13 RAM-warning fix: `check_available_ram()` was
  only reachable through `setup_ollama()`, which is skipped whenever Ollama is already
  running (the common case on any run after the first) — so the warning never actually
  fired in practice. Moved the check to run unconditionally in `ensure_ollama_ready()`.
  Confirmed via today's log that RAM had dropped to 0.27GB free (96.5% used) with no
  warning shown.
- Noted for follow-up: today's log ends on an unresolved "Move new_notes.txt into the
  test directory" prompt with no logged tool call or response — needs manual retest.

### Commit
fix: correct model-identity answers and re-fire RAM warning on repeat runs; strengthen anti-tool-call guidance for greetings

---

## 2026-08-15

### Completed
- Added evaluation dataset
- Improved logger
- Fixed Windows path issue

### Commit
fix: improve Windows compatibility