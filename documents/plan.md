# CLI Agent Development Plan

> Version: 1.0
> Target Platform: Windows
> LLM Runtime: Ollama
> Default Model: Qwen 2.5
> Future Goal: Secure Voice-enabled Local AI Assistant

---

# Vision

Build a secure, modular, local-first AI CLI Agent capable of:

- Understanding natural language
- Executing local tools
- Following security policies
- Working offline
- Supporting voice interaction
- Extensible through plugins/tools
- Acting as a local coding assistant

This project should be designed similarly to professional AI coding agents instead of being a single Python script.

---

# High Level Architecture

```
                 User
                   │
      ┌────────────┴─────────────┐
      │                          │
      ▼                          ▼
    CLI                     Voice Interface
      │                          │
      └────────────┬─────────────┘
                   │
                   ▼
            Conversation Manager
                   │
                   ▼
             Ollama Client
                   │
                   ▼
            Tool Dispatcher
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
 Policy Engine          Tool Registry
        │                     │
        ▼                     ▼
 Permission Check     Individual Tools
        │
        ▼
 Windows Operating System
```

---

# Development Roadmap

## Phase 1

Basic CLI Agent

Goal:

Create a conversational terminal assistant using Ollama.

Features

- Chat
- Conversation memory
- System prompt
- Exit command

No tools.

---

## Phase 2

Tool Calling

Goal

Allow the LLM to invoke Python functions.

Example

User

> Show current directory

↓

LLM

↓

read_directory()

↓

Python Tool

↓

JSON

↓

LLM Response

---

## Phase 3

Filesystem Tools

Implement dedicated tools.

Never expose unrestricted shell execution.

Initial tools:

```
read_directory.py
read_file.py
search_files.py
system_info.py
git_status.py
python_runner.py
```

---

## Phase 4

Policy Engine

Every tool request must go through:

```
LLM

↓

Policy Engine

↓

Allow?

↓

Execute Tool
```

The LLM NEVER directly executes commands.

---

## Phase 5

Permission Levels

Level 0

Chat only

Examples

- General questions
- Coding help

---

Level 1

Read Only

Allowed

- Read files
- List folders
- Search
- Git status
- System information

Auto execute.

---

Level 2

Workspace Write

Requires owner approval.

Examples

- Create file
- Rename
- Move
- Copy

---

Level 3

System Write

Requires explicit approval.

Examples

- pip install
- git commit
- git push
- create virtual environment

---

Level 4

Dangerous

Never execute automatically.

Examples

- delete
- shutdown
- registry
- diskpart
- format
- taskkill

---

# Workspace Restriction

Only allow writing inside

```
C:\Users\<User>\Projects
```

Protected

```
Windows
Program Files
AppData
System32
Registry
```

Read access may be allowed.

Write/Delete must be blocked.

---

# Folder Structure

```
cli_agent/

│
├── cliagent.py
├── config.py
├── tool_registry.py
├── policy_engine.py
├── ollama_client.py
├── conversation.py
├── tool_executor.py
├── logger.py
│
├── tools/
│   ├── __init__.py
│   ├── read_directory.py
│   ├── read_file.py
│   ├── search_files.py
│   ├── create_file.py
│   ├── write_file.py
│   ├── delete_file.py
│   ├── git_status.py
│   ├── system_info.py
│   └── ...
│
├── voice/
│
├── config/
│   ├── models.json
│   └── policy.json
│
└── logs/
```

---

# Responsibility of Each File

## cliagent.py

Application entry point.

Responsibilities

- Start application
- Initialize conversation
- Start event loop

Should remain very small.

---

## ollama_client.py

Responsible for

- Sending messages
- Receiving responses
- Handling tool calls

No business logic.

---

## conversation.py

Maintains

```
messages = []
```

Provides methods

```
add_user()

add_assistant()

add_tool()

history()
```

---

## tool_executor.py

Responsible for

Executing Python tools.

No policy logic.

---

## policy_engine.py

Responsible for

Permission checks.

Example

```
Request

↓

Allowed?

↓

Execute

OR

Reject
```

---

## logger.py

Responsible for

Logging

```
User Prompt

Tool

Arguments

Output

Timestamp
```

---

# Tool Design Principles

Every tool should

✔ Do ONE thing only

✔ Return JSON

✔ Never print

✔ Never trust user input

✔ Never bypass policy

---

Example

```
read_directory.py
```

Only

```
Read folders
```

Never

```
Delete

Rename

Move
```

---

# Tool Registration

Each tool has

Python Function

```
def read_directory(...)
```

Registered in

```
tool_registry.py
```

Example

```
TOOL_MAP = {

    "read_directory": read_directory

}
```

Tool Schema

```
TOOLS_SCHEMA = [

    {
        ...
    }

]
```

cliagent.py imports

```
TOOL_MAP

TOOLS_SCHEMA
```

Nothing else.

---

# Preferred Tool Categories

Filesystem

```
read_directory

read_file

write_file

create_file

rename_file

copy_file

move_file

delete_file
```

---

Search

```
search_files

search_text
```

---

Git

```
git_status

git_log

git_diff

git_commit

git_push
```

---

Python

```
run_python

run_tests

run_script
```

---

System

```
system_info

disk_info

network_info

process_info
```

---

Package Manager

```
pip_install

pip_list
```

---

Terminal

```
execute_shell_command
```

Last resort only.

---

# Tool Metadata

Instead of

```
TOOL_MAP = {

    "read_directory": read_directory

}
```

Use

```
TOOL_MAP = {

    "read_directory": {

        "function": read_directory,

        "permission": "read",

        "category": "filesystem"

    }

}
```

Advantages

- Easier permissions
- Better logging
- Future GUI support

---

# Logging

Every action

```
Timestamp

User Prompt

Tool

Arguments

Permission

Output

Execution Time
```

Stored

```
logs/agent.log
```

---

# Security Rules

Never allow

```
format

shutdown

diskpart

regedit

bcdedit

cipher

taskkill

del Windows

rm -rf
```

Without explicit owner approval.

---

Protected Paths

```
Windows

Program Files

System32

AppData
```

---

# Model Management

Use only Qwen models.

```
config/models.json
```

Example

```
{
  "default":"qwen2.5:1.5b",
  "allowed":[
      "qwen2.5:0.5b",
      "qwen2.5:1.5b",
      "qwen2.5:3b"
  ]
}
```

Future

Auto detect RAM

↓

Choose appropriate model

---

# Voice Agent Roadmap

Current

```
Keyboard

↓

CLI
```

Future

```
Microphone

↓

Speech To Text

↓

CLI Agent

↓

Tool Execution

↓

LLM

↓

Text To Speech

↓

Speaker
```

---

# Testing Checklist

Conversation

- Hello
- Explain Python

Filesystem

- List directory
- Read file
- Search file

System

- RAM
- CPU
- Python version

Git

- Status
- Log

Policy

- Create file
- Delete file
- Rename file

Dangerous Commands

- Delete Windows
- Shutdown
- Registry

Should all be blocked.

---

# Long-Term Vision

The final project should evolve from

```
Simple CLI Chatbot
```

↓

```
Secure CLI Assistant
```

↓

```
Local Coding Assistant
```

↓

```
Voice Controlled AI Assistant
```

↓

```
Plugin-based Local AI Operating System
```

The architecture should remain modular so that adding a new capability only requires:

1. Creating a new tool.
2. Registering it in `tool_registry.py`.
3. Defining its permission level in `policy_engine.py`.

No changes should be required to the main application loop.