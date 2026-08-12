"""
Smoke tests for newly implemented tools.

Tests basic functionality of:
- network_info.py
- edit_file.py
- terminal_read.py
- process_manager.py
- service_manager.py
- install_package.py
- tools.py
"""

import json
import sys
import tempfile
from pathlib import Path

# Force UTF-8 output encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def test_tool(tool_name, func, args, expect_success=True):
    """Test a single tool function."""
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print(f"{'='*60}")

    try:
        result_json = func(*args) if isinstance(args, list) else func(**args)
        result = json.loads(result_json)

        print(f"Result: {json.dumps(result, indent=2)}")

        if expect_success:
            assert result.get("success") == True, f"Expected success=True, got {result.get('success')}"
            print(f"[OK] PASS: {tool_name}")
        else:
            assert result.get("success") == False, f"Expected success=False, got {result.get('success')}"
            print(f"[OK] PASS: {tool_name} (expected failure)")

        return True
    except AssertionError as e:
        print(f"[FAIL] FAIL: {tool_name}")
        print(f"   Assertion: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] ERROR: {tool_name}")
        print(f"   Exception: {e}")
        return False


def main():
    """Run all smoke tests."""
    print("\n" + "="*60)
    print("SMOKE TESTS: New Tool Implementations")
    print("="*60)

    passed = 0
    failed = 0

    # Test 1: tools.py - get_tool_info
    print("\n--- Test Suite 1: tools.py ---")
    from tools.tools import get_tool_info

    if test_tool("get_tool_info", get_tool_info, []):
        passed += 1
    else:
        failed += 1

    # Test 2: network_info.py
    print("\n--- Test Suite 2: network_info.py ---")
    from tools.network_info import network_info, ping, dns_lookup, check_port

    if test_tool("network_info", network_info, []):
        passed += 1
    else:
        failed += 1

    if test_tool("dns_lookup (localhost)", dns_lookup, ["localhost"]):
        passed += 1
    else:
        failed += 1

    # Note: ping and check_port may fail in isolated environments
    # Just test they don't crash
    try:
        result = json.loads(ping("127.0.0.1", 1))
        print(f"\nping (loopback): {json.dumps(result, indent=2)}")
        print("[OK] PASS: ping (no crash)")
        passed += 1
    except Exception as e:
        print(f"[SKIP] SKIP: ping (network might be unavailable: {e})")

    try:
        result = json.loads(check_port("localhost", 22))
        print(f"\ncheck_port (localhost:22): {json.dumps(result, indent=2)}")
        print("[OK] PASS: check_port (no crash)")
        passed += 1
    except Exception as e:
        print(f"[ERROR] ERROR: check_port: {e}")
        failed += 1

    # Test 3: edit_file.py
    print("\n--- Test Suite 3: edit_file.py ---")
    from tools.edit_file import edit_file, insert_line, delete_line

    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        test_file = f.name
        f.write("Line 1\nLine 2\nLine 3\n")

    try:
        # Test edit_file
        if test_tool("edit_file (find/replace)", edit_file, [test_file, "Line 2", "Modified Line 2"]):
            passed += 1
        else:
            failed += 1

        # Verify the edit
        with open(test_file, "r") as f:
            content = f.read()
            assert "Modified Line 2" in content, "Edit failed to update file"
            print(f"[OK] Verification: File content updated correctly")

        # Test insert_line
        with open(test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        if test_tool("insert_line", insert_line, [test_file, 2, "Inserted Line"]):
            passed += 1
        else:
            failed += 1

        # Test delete_line
        if test_tool("delete_line", delete_line, [test_file, 2]):
            passed += 1
        else:
            failed += 1

    finally:
        Path(test_file).unlink()

    # Test 4: terminal_read.py
    print("\n--- Test Suite 4: terminal_read.py ---")
    from tools.terminal_read import run_command, get_output

    # Test with a simple command
    if sys.platform == "win32":
        if test_tool("run_command (whoami)", run_command, ["whoami", ".", True]):
            passed += 1
        else:
            failed += 1

        if test_tool("get_output (echo)", get_output, ["echo hello"]):
            passed += 1
        else:
            failed += 1
    else:
        if test_tool("run_command (whoami)", run_command, ["whoami", ".", False]):
            passed += 1
        else:
            failed += 1

        if test_tool("get_output (echo)", get_output, ["echo hello"]):
            passed += 1
        else:
            failed += 1

    # Test 5: process_manager.py
    print("\n--- Test Suite 5: process_manager.py ---")
    from tools.process_manager import list_processes, find_process_by_name

    if test_tool("list_processes", list_processes, []):
        passed += 1
    else:
        failed += 1

    if test_tool("find_process_by_name (python)", find_process_by_name, ["python"]):
        passed += 1
    else:
        failed += 1

    # Test 6: service_manager.py (Windows only)
    print("\n--- Test Suite 6: service_manager.py ---")
    from tools.service_manager import is_windows

    if is_windows():
        from tools.service_manager import list_services

        if test_tool("list_services", list_services, []):
            passed += 1
        else:
            failed += 1
    else:
        print("[SKIP] SKIP: Service management tests (not on Windows)")

    # Test 7: install_package.py
    print("\n--- Test Suite 7: install_package.py ---")
    from tools.install_package import list_installed_packages

    if test_tool("list_installed_packages", list_installed_packages, []):
        passed += 1
    else:
        failed += 1

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"[OK] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    print(f"Total: {passed + failed}")
    print("="*60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
