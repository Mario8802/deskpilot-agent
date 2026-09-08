from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Task:
    id: int | None
    prompt: str
    run_at: datetime
    status: str = "pending"
    created_at: datetime | None = None
    last_error: str | None = None


@dataclass(slots=True)
class PlanStep:
    action: str
    args: dict[str, Any]
