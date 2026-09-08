from datetime import datetime
import time

from .actions import ActionExecutor
from .ollama import OllamaClient
from .store import TaskStore


class AgentRunner:
    def __init__(self, store: TaskStore, ollama: OllamaClient, executor: ActionExecutor):
        self.store = store
        self.ollama = ollama
        self.executor = executor

    def run_due(self, execute: bool = False) -> int:
        tasks = self.store.due(datetime.now())
        for task in tasks:
            assert task.id is not None
            self.store.set_status(task.id, "running")
            self.store.audit(task.id, "task_started", task.prompt)
            try:
                plan = self.ollama.plan(task.prompt)
                self.store.audit(task.id, "plan_created", repr(plan))
                for step in plan:
                    result = self.executor.execute(step, dry_run=not execute)
                    self.store.audit(task.id, "action_result", result)
                    print(f"Task {task.id}: {result}")
                self.store.set_status(task.id, "done")
                self.store.audit(task.id, "task_done")
            except Exception as exc:
                self.store.set_status(task.id, "failed", str(exc))
                self.store.audit(task.id, "task_failed", str(exc))
                print(f"Task {task.id} failed: {exc}")
        return len(tasks)

    def daemon(self, execute: bool = False, interval: int = 10) -> None:
        print(f"DeskPilot daemon started. execute={execute}, interval={interval}s")
        while True:
            self.run_due(execute=execute)
            time.sleep(interval)
