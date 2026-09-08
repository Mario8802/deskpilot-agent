# Architecture

DeskPilot intentionally separates **planning** from **execution**.

```text
Human CLI request
      |
      v
SQLite task store
      |
      v
Scheduler / runner
      |
      v
Ollama planner ----> local LLM
      |
      v
Validated JSON plan
      |
      v
Allowlisted action executor
   /    |       |       \
 URL   note    app     Ollama
      |
      v
Audit log in SQLite
```

## Why not let the LLM run arbitrary shell commands?

Because an LLM can misunderstand instructions or be manipulated by untrusted content. The prototype therefore accepts only a small action vocabulary and validates each action before execution.

## Why SQLite?

This is a single-computer learning prototype. SQLite keeps the whole database in one local file and needs no database server. A future multi-user Django control plane could replace it with PostgreSQL.

## Why not Docker for desktop control?

Docker is excellent for servers, but a container is isolated from the Windows desktop. A local desktop agent that must open Notepad or a browser should normally run on the host OS. Ollama can also run on the host and expose its local HTTP API.

## Power and wake behavior

Software cannot run while a computer is fully powered off. Options are:

- keep Windows in sleep and use Task Scheduler with WakeToRun;
- configure BIOS/UEFI RTC wake;
- use Wake-on-LAN from another always-on device;
- run the agent on an always-on server/cloud machine instead.
