# DeskPilot Agent

A small, inspectable **local-first scheduled desktop AI agent** for learning how AI planning, scheduling, local LLMs, persistence, and safe computer actions fit together.

The goal is to prototype the idea:

> "Tomorrow at 06:00, do this on my computer."

without giving an LLM unrestricted control of the machine.

## What it does

- stores scheduled tasks in SQLite;
- understands `tomorrow 06:00` and ISO date/time input;
- asks a local Ollama model to turn a task into a structured JSON plan;
- executes only a tiny allowlist of actions;
- defaults to **dry-run**;
- records task state and audit events;
- can run continuously as a local daemon;
- includes a Windows Task Scheduler helper script.

Current allowlisted actions:

- `open_url`
- `write_note`
- `launch_app` (`notepad` / `calculator` by default)
- `ask_ollama`

There is deliberately **no arbitrary shell execution**, registry editing, credential access, file deletion, or unrestricted code execution.

## Architecture

```text
You
 |
 | deskpilot add --at "tomorrow 06:00" --prompt "Open example.com"
 v
SQLite database
 |
 v
DeskPilot scheduler
 |
 v
Ollama local API (127.0.0.1:11434)
 |
 v
Local LLM creates JSON plan
 |
 v
Safety validator / allowlist
 |
 +----> Browser
 +----> Notepad / Calculator
 +----> workspace notes
 +----> Ollama
 |
 v
Audit log
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the reasoning behind the design.

## Requirements

- Python 3.11+
- Ollama installed locally
- one Ollama model, for example a small Qwen/Gemma model appropriate for your hardware

## Quick start

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Start Ollama and make sure a model is installed. Set the model name if needed:

```powershell
$env:OLLAMA_MODEL="qwen3:4b"
```

Schedule a task:

```powershell
deskpilot add --at "tomorrow 06:00" --prompt "Open https://www.python.org and launch calculator"
```

List tasks:

```powershell
deskpilot list
```

Test due tasks in safe dry-run mode:

```powershell
deskpilot run-once
```

Actually execute allowlisted actions:

```powershell
deskpilot run-once --execute
```

Run continuously:

```powershell
deskpilot daemon --execute
```

## Example of what Ollama is asked to produce

```json
{
  "steps": [
    {
      "action": "open_url",
      "args": {"url": "https://www.python.org"}
    },
    {
      "action": "launch_app",
      "args": {"app": "calculator"}
    }
  ]
}
```

DeskPilot validates this structure before doing anything.

## Windows startup

`scripts/install_windows_daemon.ps1` demonstrates how to register the agent with Windows Task Scheduler so it starts after logon.

Run PowerShell as yourself from the project directory and review the script before using it.

Important: **a fully powered-off PC cannot execute Python code.** To wake at a specific time, use Windows sleep + Task Scheduler `WakeToRun`, BIOS/UEFI RTC wake, Wake-on-LAN, or an always-on machine.

## Database

The prototype uses `sqlite3`, included with Python. The default DB file is:

```text
deskpilot.db
```

It contains:

- `tasks` — what should run and when;
- `audit_log` — what the agent planned and executed.

This is intentionally simpler than PostgreSQL because the MVP runs on one PC. A future server version can use Django + PostgreSQL.

## Ollama

Ollama is the local LLM server. DeskPilot sends HTTP requests to:

```text
http://127.0.0.1:11434/api/chat
```

So the flow is:

```text
DeskPilot Python process
        |
        | local HTTP request
        v
Ollama
        |
        v
local model
```

No OpenAI API key is required for this prototype.

## Safety model

The most important design choice is:

```text
LLM proposes actions
        |
        v
Python validates them
        |
        v
only allowlisted actions execute
```

Do not replace this with unrestricted `shell=True` or direct execution of LLM-generated commands on a real machine.

## Tests

```powershell
python -m pip install pytest
pytest
```

The tests cover:

- time parsing;
- SQLite task persistence;
- dry-run behavior;
- workspace write boundaries;
- rejection of non-allowlisted actions.

## Suggested next versions

### v0.2

- small Django dashboard;
- PostgreSQL instead of SQLite;
- REST API;
- task approval screen;
- richer audit UI.
