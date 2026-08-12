# Workspace Configuration Guide

## Overview

The Local CLI Agent uses a **workspace boundary** security policy to restrict file operations to a specific directory. This prevents accidental or malicious modifications to system directories.

---

## Current Configuration

**Workspace Root**: `E:\My Projects\local_cli_agent`

This is set in `config/policy.json`:
```json
{
  "workspace_subpath": "E:\\My Projects\\local_cli_agent"
}
```

---

## How It Works

### Path Resolution

When you specify a file path (e.g., `create_file("sample.txt", "content")`):

1. **Absolute paths** are resolved as-is
   - `E:\My Projects\local_cli_agent\sample.txt` → allowed ✅
   - `C:\Windows\file.txt` → blocked ❌

2. **Relative paths** are resolved relative to current working directory
   - `sample.txt` → becomes `E:\My Projects\local_cli_agent\sample.txt` → allowed ✅
   - `logs/debug.log` → becomes `E:\My Projects\local_cli_agent\logs\debug.log` → allowed ✅

3. **Home directory shortcuts** are expanded
   - `~/file.txt` → becomes `C:\Users\Shri\file.txt` → checked against workspace ✅/❌

### Validation Logic

The `is_inside_workspace()` function (in `tools/path_utils.py`) checks:
```python
def is_inside_workspace(path: Path) -> bool:
    workspace = get_workspace()
    try:
        path.resolve().relative_to(workspace)
        return True
    except ValueError:
        return False
```

If the path cannot be expressed as relative to the workspace, it's blocked.

---

## Changing the Workspace

### Option 1: Absolute Path (Recommended for Non-Standard Locations)

Edit `config/policy.json`:
```json
{
  "workspace_subpath": "E:\\Path\\To\\Your\\Project"
}
```

The config now supports absolute paths. In `config.py`:
```python
def get_workspace_root() -> Path:
    subpath = POLICY_CONFIG.get("workspace_subpath", "Projects")
    if Path(subpath).is_absolute():
        return Path(subpath)
    return Path.home() / subpath
```

### Option 2: Relative Path (For ~/Projects Folder)

Edit `config/policy.json`:
```json
{
  "workspace_subpath": "Projects"
}
```

This resolves to `C:\Users\Shri\Projects` (or your home directory).

### Option 3: Dynamic Configuration

Create a `.env` file in the project root:
```
WORKSPACE_ROOT=E:\My Projects\local_cli_agent
```

Then update `config.py` to load from environment:
```python
def get_workspace_root() -> Path:
    from dotenv import load_dotenv
    load_dotenv()
    subpath = os.getenv("WORKSPACE_ROOT") or POLICY_CONFIG.get("workspace_subpath", "Projects")
    if Path(subpath).is_absolute():
        return Path(subpath)
    return Path.home() / subpath
```

---

## Security: Protected Paths

Even within the workspace, certain paths are blocked:

**Protected Path Names** (in `config/policy.json`):
- Windows
- System32
- Program Files
- Program Files (x86)
- AppData

**Why?** These Windows system directories exist everywhere, so blocking by name prevents accidental damage.

Example:
- ✅ `E:\My Projects\local_cli_agent\Windows\backup.txt` → allowed (within workspace)
- ❌ `C:\Windows\file.txt` → blocked (protected system path)
- ❌ `E:\Program Files\something.txt` → blocked (protected path name)

---

## Permission Levels

### Read (Auto-Approved)
- `read_file`, `read_directory`, `search_files`, `git_status`
- No workspace restriction

### Workspace Write (Requires Approval)
- `create_file`, `write_file`, `edit_file`, `insert_line`, `delete_line`
- **Must be inside workspace boundary**
- User can approve on each use

### System Write (Requires Approval)
- `git_commit`, `git_push`, `pip_install`, `run_script`
- No workspace boundary check (system-wide operations)
- User must approve

### Dangerous (Requires Typed Approval)
- `delete_file`, `kill_process`
- **Must be inside workspace boundary** (for delete_file)
- User must type confirmation

---

## Common Issues & Solutions

### Issue: "Write operations restricted to workspace"

**Symptom**: Agent refuses to create files, saying the workspace is too restrictive

**Solution**:
1. Check current workspace: `python -c "from config import get_workspace_root; print(get_workspace_root())"`
2. Update `config/policy.json` if needed
3. Restart the agent process

### Issue: Agent Suggests Wrong Paths

**Symptom**: Agent suggests creating files outside the actual workspace

**Solution**:
- The system prompt now includes the workspace path
- If the agent is still confused, it may be using a cached prompt
- **Restart the agent**: `python CLIagent.py`

### Issue: Python Caching Old Config

**Symptom**: Changes to `policy.json` don't take effect

**Solution**:
1. Kill the agent process completely
2. Clear Python cache: `find . -type d -name __pycache__ -exec rm -rf {} +` (Linux/Mac) or `Remove-Item -Recurse __pycache__` (PowerShell)
3. Restart: `python CLIagent.py`

---

## Testing Your Workspace Configuration

### Verify Workspace Path
```bash
python -c "
from config import get_workspace_root
from tools.path_utils import is_inside_workspace
from pathlib import Path

workspace = get_workspace_root()
print(f'Workspace: {workspace}')
print(f'Exists: {workspace.exists()}')

# Test paths
test_paths = [
    'sample.txt',
    str(workspace / 'file.txt'),
    'C:\\Windows\\file.txt',
    str(Path.home() / 'file.txt')
]

for path in test_paths:
    result = is_inside_workspace(Path(path))
    print(f'{path}: {result}')
"
```

### Create Test File
```bash
python -c "
from tools.create_file import create_file
import json

result = json.loads(create_file('test.txt', 'test content'))
print(json.dumps(result, indent=2))
"
```

---

## Disabling Workspace Boundary (Not Recommended)

To allow writes anywhere (dangerous for security):

Edit `policy_engine.py`, comment out line 81:
```python
# if permission == "workspace_write" and not is_inside_workspace(path):
#     return f"Write operations restricted to workspace: {get_workspace()}"
```

**Warning**: This allows the agent to modify any file on the system, including Windows system files. Only do this for testing in isolated environments.

---

## Best Practices

1. **Keep workspace separate from system directories**: Use a dedicated `Projects` folder
2. **Use relative paths**: Let the agent resolve paths naturally (`logs/file.txt` instead of full paths)
3. **Review policy changes**: When updating `policy.json`, restart the agent and test
4. **Document your setup**: Add a comment to `policy.json` explaining why you configured the workspace as you did
5. **Audit workspace changes**: Check `logs/agent_*.txt` for all file operations

---

## References

- **Config**: `config/policy.json` — Workspace subpath and security settings
- **Code**: `config.py` — `get_workspace_root()` function
- **Validation**: `tools/path_utils.py` — `is_inside_workspace()` function
- **Policy**: `policy_engine.py` — Permission checking logic
