from datetime import datetime, timedelta

from deskpilot.models import Task
from deskpilot.store import TaskStore


def test_add_and_due(tmp_path):
    store = TaskStore(tmp_path / "test.db")
    task_id = store.add(Task(id=None, prompt="open calculator", run_at=datetime.now() - timedelta(seconds=1)))
    due = store.due(datetime.now())
    assert due[0].id == task_id
    assert due[0].prompt == "open calculator"
