from datetime import datetime

from deskpilot.timeparse import parse_when


def test_tomorrow_time():
    now = datetime(2026, 9, 8, 21, 0)
    assert parse_when("tomorrow 06:00", now) == datetime(2026, 9, 9, 6, 0)


def test_iso_time():
    assert parse_when("2026-09-10T07:30") == datetime(2026, 9, 10, 7, 30)
