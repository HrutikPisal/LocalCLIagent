# Automated Evaluation Dataset Workflow

How to run `tests/cli_agent_evaluation_dataset.json` (or any batch of test
questions) against the live agent unattended, with results landing in the
real activity logs for later review. This captures the approach used for the
full 50-test run on 2026-08-19.

## Why not just pipe questions into `python CLIagent.py`?

Piping stdin into the interactive CLI works for a handful of questions, but
breaks down at scale:

- Approval prompts (`[y/N]`) are also `input()` calls on the same stdin
  stream, interleaved with the next question. Getting the count of expected
  `y`/`n` lines exactly right per question, in advance, for dozens of
  questions is fragile — one miscount desyncs everything after it.
- No way to isolate one test's failure from the rest of the batch.
- No way to special-case a single test's approval response (e.g. testing
  denial) without breaking the stdin sequence for every other test.

Instead, drive the real classes directly:

```python
import tool_executor
from conversation import Conversation
from ollama_client import OllamaClient

# Auto-approve every [y/N] prompt (equivalent to the user typing 'y').
def _approval(tool_name, arguments, reason):
    return True
tool_executor.ToolExecutor._prompt_for_approval = staticmethod(_approval)

conv = Conversation()
client = OllamaClient(conv)
conv.add_user(question)
client.logger.log_prompt(question)   # matches what run() does before _complete_turn()
reply = client._complete_turn()
```

This uses the exact same `OllamaClient`, `Conversation`, `ToolExecutor`, and
`AgentLogger` that `CLIagent.py` uses — so every prompt, tool execution, and
response is written to the real `logs/agent_<DD_MM_YYYY>.txt`, indistinguishable
from a real interactive session when reviewed later. `AgentLogger` already
supports source-tagging (see `logger.py`'s `source` parameter, `tool_executor.py`'s
`ToolExecutor(log_source=...)`) if you want to distinguish an automated run
from real usage in the log stream.

## Per-test isolation

Give each test a **fresh** `Conversation()` + `OllamaClient()`, not one
continuous conversation across all tests. Reasons:
- Matches how a real user would test different, unrelated scenarios.
- Keeps one slow/large tool result from bloating context for later tests.
- Each test's outcome is independently interpretable in the log.

Wrap each test in its own `try/except` so one exception (or one truly stuck
turn) doesn't take down the whole batch — log it and move to the next test.

## Self-terminating turns — no external timeout needed

`OllamaClient.MAX_TURN_SECONDS` (in `ollama_client.py`) is a hard ceiling
already built into `_complete_turn()`/`_stream_chat()` — every turn returns a
real string (even if just a timeout message) within that many seconds, no
matter how slow or stuck the model gets. Don't layer a second, separate
timeout on top in the runner script; it's redundant and only risks fighting
the real safety net. If turns are getting cut off before finishing on your
hardware, raise `MAX_TURN_SECONDS` itself first (see the file's own comment
for how that value was calibrated) rather than adding an orchestration-level
override that would be untested and could add a new failure mode.

## Approval handling, including special cases

The default is auto-approve-everything, but check the dataset for
tests that need something different **before** running:

- Look for an explicit field the dataset itself uses to signal a different
  expected response, e.g. this dataset's `simulated_user_approval_input: "n"`
  on one test — that test exists specifically to verify denial behavior, so
  honor it rather than blanket-approving.
- Any test whose real-world side effect is undesirable to actually trigger
  (see next section) can be approval-*denied* instead of skipped entirely —
  this still exercises tool-selection and the approval-gate code path
  without letting the underlying action actually run.

Implement this with a small per-test override map keyed by test ID, checked
inside the monkeypatched `_prompt_for_approval`:

```python
DENY_IDS = {"T015", "T032"}  # example — decide per dataset
current_test_id = {"id": None}

def _approval(tool_name, arguments, reason):
    return current_test_id["id"] not in DENY_IDS
```

## Real-world side effects — decide these BEFORE running, every time

Auto-approving everything blindly is dangerous for certain tool categories.
**Always scan the dataset for these before a run, and get explicit sign-off
on each — do not assume last time's answers still apply:**

| Category | Real effect if auto-approved | Typical handling |
|---|---|---|
| `git_commit` / `git_push` | Really commits/pushes to the actual repo, potentially including unrelated uncommitted files sitting in the workspace at the time | Usually skip entirely — these test policy/tool-selection, not something worth risking on a real repo |
| `pip_install` / `install_package` / `install_requirements` | Really installs into the live Python environment | Usually approval-deny (tests the path without the side effect) |
| `start_service` / `stop_service` / `restart_service` | Real, live change to a running Windows service | Prefer read-only checks (`get_service_status`) or fake service names; only test a real state change with explicit, specific sign-off |
| `kill_process` | Terminates a real process if the PID happens to be valid | Low risk if the test uses an implausible/arbitrary PID, but confirm before running against a real, currently-valid PID |
| `delete_file` | Permanently deletes a real file | Fine to auto-approve against fixture files created for the test; never against real project files without checking first |

## Fictional/fixture-dependent test data

A dataset written against a hypothetical workspace (different username,
different project layout, files that don't exist in your real project) will
have some tests hit a natural "file not found" instead of their intended
success path. Two options, decide explicitly:

1. **Run as-is** — simpler, zero setup risk, but some tests end up exercising
   a different code path (the error-handling path) than originally intended.
2. **Create matching fixture files first** — more faithful to the dataset's
   intent, but:
   - Adds real files to the actual project directory (clean these up
     afterward if they're not meant to be permanent, e.g. `huge_dump.sql`).
   - Watch for **sequential collisions** between tests that aren't designed
     to run back-to-back in one continuous session — e.g. a test that creates
     `notes.txt`, followed later by a different test that tries to rename
     something else *to* `notes.txt`, will hit a real "already exists"
     conflict from the first test's leftover state, even though each test
     was independently written assuming a fresh starting point. This isn't a
     bug — it's a genuine, different outcome than the dataset's isolated
     scenario intended. Note it in the report rather than trying to
     perfectly reset file state between every single test (that adds
     significant complexity and its own risk of deleting something real).

## Interpreting results — reference data, not literal fixtures

A dataset's `expected_tool_output` / `expected_llm_response` fields describe
what a *correct* response looks like in an equivalent scenario — they are
not literal values the live system must reproduce byte-for-byte (paths,
hostnames, timestamps will legitimately differ from whatever hypothetical
example data the dataset used). Evaluate against the dataset's own
`validation` block instead:
- `tool_selected` / `expected_tool`: did it call the right tool (or
  correctly call none)?
- `hallucination_allowed: false`: does the response only state values that
  actually appear in the real tool output it received?
- `requires_confirmation`: did an approval prompt correctly appear (or not)?
- `grounding_check` / `policy_note` (if present): tests a specific, named
  failure mode — read it, it usually explains exactly what to look for.

Also check whether the codebase has grown capability since the dataset was
written — this dataset explicitly flags a few tests (`not_implemented_note`)
as expected to start "failing" (in a good way) once a placeholder tool gets
implemented. A test's real-world behavior changing for the better isn't a
regression; check the dataset's own notes before treating a mismatch as a
problem.

## Checklist for running this again

1. Read the full dataset first. Identify: any real-side-effect tool
   categories (table above), any dataset-fixture files needed, any explicit
   special-case fields (like `simulated_user_approval_input`).
2. Ask the user explicitly about each real-side-effect category found — do
   not reuse a previous run's answers without asking again.
3. Create needed fixture files; note any sequential-collision risks.
4. Confirm Ollama is running and check available RAM before starting a long
   batch — on constrained hardware, a multi-hour run can hit resource
   pressure partway through; know the current baseline before you start so a
   mid-run problem is easy to recognize.
5. Write a runner script following the pattern above: load the dataset,
   filter out excluded IDs, per-test fresh Conversation + isolated
   try/except, approval override map, real logger.
6. Launch as a background process so it doesn't block. Redirect stdout to a
   file, but remember Python buffers stdout when it's not a TTY — the *real*
   evidence of progress is the live `logs/agent_<date>.txt` file, not the
   runner's own redirected output, which may show nothing until the process
   exits.
7. When it finishes, cross-reference the runner's own summary against the
   raw `logs/agent_*.txt` entries (tool arguments, full JSON tool output) —
   the summary alone truncates responses and doesn't show tool call
   arguments, which is often exactly what you need to diagnose a surprising
   result.
