from pathlib import Path

import pytest

from deskpilot.actions import ActionExecutor, ActionRejected
from deskpilot.config import Settings
from deskpilot.models import PlanStep


class FakeOllama:
    def chat(self, prompt: str) -> str:
        return f"answer:{prompt}"


def make_executor(tmp_path: Path) -> ActionExecutor:
    settings = Settings(workspace=tmp_path / "workspace", allowed_apps=("notepad",))
    return ActionExecutor(settings, FakeOllama())


def test_dry_run_does_not_write(tmp_path):
    executor = make_executor(tmp_path)
    result = executor.execute(PlanStep("write_note", {"filename": "x.txt", "content": "hello"}), dry_run=True)
    assert result.startswith("DRY-RUN")
    assert not (tmp_path / "workspace" / "x.txt").exists()


def test_write_note_stays_in_workspace(tmp_path):
    executor = make_executor(tmp_path)
    executor.execute(PlanStep("write_note", {"filename": "note.txt", "content": "hello"}), dry_run=False)
    assert (tmp_path / "workspace" / "note.txt").read_text(encoding="utf-8") == "hello"


def test_rejects_unknown_action(tmp_path):
    executor = make_executor(tmp_path)
    with pytest.raises(ActionRejected):
        executor.execute(PlanStep("run_shell", {"cmd": "whoami"}), dry_run=False)
