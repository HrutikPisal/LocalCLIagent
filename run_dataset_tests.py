"""
Run all 50 test cases from cli_agent_evaluation_dataset.json sequentially.
Save each question + response to a separate .txt file in tests/results/ folder.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

DATASET_FILE = "tests/cli_agent_evaluation_dataset.json"
RESULTS_DIR = Path("tests/results")
RESULTS_DIR.mkdir(exist_ok=True)

# Load test cases
with open(DATASET_FILE, encoding="utf-8") as f:
    test_cases = json.load(f)

print(f"Loaded {len(test_cases)} test cases from {DATASET_FILE}")
print(f"Results will be saved to: {RESULTS_DIR.absolute()}\n")

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    test_id = test.get("id", f"T{i:03d}")
    question = test.get("cli_user_query", "")
    category = test.get("category", "Unknown")

    print(f"[{i}/50] {test_id} ({category})")
    print(f"  Question: {question[:60]}...")

    # Feed question to CLIagent via stdin, capture output
    try:
        # Send question + exit to CLIagent
        input_text = f"{question}\nexit\n"
        result = subprocess.run(
            [sys.executable, "CLIagent.py"],
            input=input_text,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Extract response (everything after the question is printed)
        output = result.stdout + result.stderr
        response = output  # Store full output for now

        # Save to file
        output_file = RESULTS_DIR / f"{test_id}_{category.replace('/', '_')}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Test ID: {test_id}\n")
            f.write(f"Category: {category}\n")
            f.write(f"Question: {question}\n")
            f.write(f"\n{'='*70}\n")
            f.write(f"RESPONSE:\n{'='*70}\n\n")
            f.write(response)
            f.write(f"\n\n{'='*70}\n")
            f.write(f"Test conducted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print(f"  [OK] Saved to: {output_file.name}")
        passed += 1

    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] Timeout (60s)")
        failed += 1
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        failed += 1

print(f"\n{'='*70}")
print(f"SUMMARY")
print(f"{'='*70}")
print(f"Total: {len(test_cases)}")
print(f"Completed: {passed}")
print(f"Failed: {failed}")
print(f"\nResults saved to: {RESULTS_DIR.absolute()}")
