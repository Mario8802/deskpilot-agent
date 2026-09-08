from datetime import datetime, timedelta
import re


def parse_when(text: str, now: datetime | None = None) -> datetime:
    """Parse either ISO local time or a small beginner-friendly natural form.

    Supported:
      2026-09-09T06:00
      tomorrow 06:00
      today 22:30
    """
    now = now or datetime.now()
    value = text.strip().lower()

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass

    match = re.fullmatch(r"(today|tomorrow)\s+(\d{1,2}):(\d{2})", value)
    if not match:
        raise ValueError("Use ISO time like 2026-09-09T06:00 or 'tomorrow 06:00'.")

    day_word, hour_text, minute_text = match.groups()
    hour, minute = int(hour_text), int(minute_text)
    if hour > 23 or minute > 59:
        raise ValueError("Invalid clock time.")

    target_date = now.date() + (timedelta(days=1) if day_word == "tomorrow" else timedelta())
    return datetime.combine(target_date, datetime.min.time()).replace(hour=hour, minute=minute)
