import argparse

from .actions import ActionExecutor
from .config import SETTINGS
from .models import Task
from .ollama import OllamaClient
from .runner import AgentRunner
from .store import TaskStore
from .timeparse import parse_when


def build_runner() -> tuple[TaskStore, AgentRunner]:
    store = TaskStore(SETTINGS.db_path)
    ollama = OllamaClient(SETTINGS.ollama_base_url, SETTINGS.ollama_model)
    executor = ActionExecutor(SETTINGS, ollama)
    return store, AgentRunner(store, ollama, executor)


def main() -> None:
    parser = argparse.ArgumentParser(prog="deskpilot", description="Local scheduled desktop AI agent")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Schedule a task")
    add.add_argument("--at", required=True, help="2026-09-09T06:00 or 'tomorrow 06:00'")
    add.add_argument("--prompt", required=True)

    sub.add_parser("list", help="List scheduled tasks")

    run_once = sub.add_parser("run-once", help="Run due tasks once")
    run_once.add_argument("--execute", action="store_true", help="Actually perform allowlisted actions")

    daemon = sub.add_parser("daemon", help="Continuously execute due tasks")
    daemon.add_argument("--execute", action="store_true", help="Actually perform allowlisted actions")
    daemon.add_argument("--interval", type=int, default=10)

    args = parser.parse_args()
    store, runner = build_runner()

    if args.command == "add":
        when = parse_when(args.at)
        task_id = store.add(Task(id=None, prompt=args.prompt, run_at=when))
        print(f"Scheduled task {task_id} for {when.isoformat(timespec='minutes')}")
    elif args.command == "list":
        tasks = store.list()
        if not tasks:
            print("No tasks.")
        for task in tasks:
            print(f"#{task.id} {task.run_at.isoformat(timespec='minutes')} [{task.status}] {task.prompt}")
    elif args.command == "run-once":
        execute = args.execute or SETTINGS.execute_enabled
        count = runner.run_due(execute=execute)
        print(f"Processed {count} due task(s).")
    elif args.command == "daemon":
        execute = args.execute or SETTINGS.execute_enabled
        runner.daemon(execute=execute, interval=max(1, args.interval))


if __name__ == "__main__":
    main()
