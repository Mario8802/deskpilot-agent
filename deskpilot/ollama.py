import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import PlanStep


SYSTEM_PROMPT = """You are a desktop task planner. Convert the user request into JSON only.
Return exactly this shape: {\"steps\": [{\"action\": \"...\", \"args\": {...}}]}.
Allowed actions are ONLY:
- open_url with args {\"url\": \"https://...\"}
- write_note with args {\"filename\": \"name.txt\", \"content\": \"...\"}
- launch_app with args {\"app\": \"notepad\"} or {\"app\": \"calculator\"}
- ask_ollama with args {\"prompt\": \"...\"}
Never request shell commands, PowerShell, registry edits, credential access, file deletion, downloads, or arbitrary code execution.
If the request cannot be expressed safely with these actions, return {\"steps\": []}.
"""


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(self, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            }
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise OllamaError(f"Ollama request failed: {exc}") from exc
        return str(data["message"]["content"])

    def plan(self, prompt: str) -> list[PlanStep]:
        raw = self.chat(prompt).strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:].strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OllamaError("Ollama did not return valid JSON plan.") from exc

        steps = data.get("steps")
        if not isinstance(steps, list):
            raise OllamaError("Plan is missing a steps list.")

        result: list[PlanStep] = []
        for item in steps:
            if not isinstance(item, dict) or not isinstance(item.get("action"), str) or not isinstance(item.get("args"), dict):
                raise OllamaError("Invalid plan step shape.")
            result.append(PlanStep(action=item["action"], args=item["args"]))
        return result
