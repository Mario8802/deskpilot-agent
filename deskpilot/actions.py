import subprocess
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

from .config import Settings
from .models import PlanStep
from .ollama import OllamaClient


class ActionRejected(RuntimeError):
    pass


class ActionExecutor:
    ALLOWED = {"open_url", "write_note", "launch_app", "ask_ollama"}

    def __init__(self, settings: Settings, ollama: OllamaClient):
        self.settings = settings
        self.ollama = ollama
        self.settings.workspace.mkdir(parents=True, exist_ok=True)

    def execute(self, step: PlanStep, dry_run: bool = True) -> str:
        if step.action not in self.ALLOWED:
            raise ActionRejected(f"Action not allowlisted: {step.action}")

        if dry_run:
            return f"DRY-RUN {step.action} {step.args}"

        handlers = {
            "open_url": self._open_url,
            "write_note": self._write_note,
            "launch_app": self._launch_app,
            "ask_ollama": self._ask_ollama,
        }
        return handlers[step.action](step.args)

    def _open_url(self, args: dict) -> str:
        url = str(args.get("url", ""))
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ActionRejected("Only http/https URLs are allowed.")
        webbrowser.open(url)
        return f"Opened {url}"

    def _write_note(self, args: dict) -> str:
        filename = Path(str(args.get("filename", "note.txt"))).name
        if not filename.lower().endswith((".txt", ".md")):
            raise ActionRejected("Notes must be .txt or .md files.")
        target = (self.settings.workspace / filename).resolve()
        workspace = self.settings.workspace.resolve()
        if workspace not in target.parents:
            raise ActionRejected("Refusing to write outside workspace.")
        content = str(args.get("content", ""))
        target.write_text(content, encoding="utf-8")
        return f"Wrote {target}"

    def _launch_app(self, args: dict) -> str:
        app = str(args.get("app", "")).lower()
        if app not in self.settings.allowed_apps:
            raise ActionRejected(f"App is not allowlisted: {app}")

        command = self._app_command(app)
        subprocess.Popen(command, shell=False)
        return f"Launched {app}"

    @staticmethod
    def _app_command(app: str) -> list[str]:
        if sys.platform.startswith("win"):
            mapping = {
                "notepad": ["notepad.exe"],
                "calculator": ["calc.exe"],
            }
        elif sys.platform == "darwin":
            mapping = {
                "notepad": ["open", "-a", "TextEdit"],
                "calculator": ["open", "-a", "Calculator"],
            }
        else:
            mapping = {
                "notepad": ["gedit"],
                "calculator": ["gnome-calculator"],
            }
        if app not in mapping:
            raise ActionRejected(f"No command mapping for {app} on this OS.")
        return mapping[app]

    def _ask_ollama(self, args: dict) -> str:
        prompt = str(args.get("prompt", "")).strip()
        if not prompt:
            raise ActionRejected("ask_ollama requires a prompt.")
        return self.ollama.chat(prompt)
