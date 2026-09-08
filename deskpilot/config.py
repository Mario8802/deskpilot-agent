import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    db_path: Path = Path(os.getenv("DESKPILOT_DB", "deskpilot.db"))
    workspace: Path = Path("workspace")
    execute_enabled: bool = os.getenv("DESKPILOT_EXECUTE", "0") == "1"
    allowed_apps: tuple[str, ...] = tuple(
        item.strip().lower()
        for item in os.getenv("DESKPILOT_ALLOWED_APPS", "notepad,calculator").split(",")
        if item.strip()
    )


SETTINGS = Settings()
