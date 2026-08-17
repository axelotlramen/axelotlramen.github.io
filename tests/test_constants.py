from datetime import datetime

import scripts.constants as constants


def _at(hour, minute=0):
    return datetime(2026, 8, 17, hour, minute, tzinfo=constants.TZ)


def test_reset_boundary_after_4am_is_today(monkeypatch):
    monkeypatch.setattr(constants, "now", lambda: _at(5))
    assert constants.daily_reset_boundary() == _at(4)


def test_reset_boundary_before_4am_is_yesterday(monkeypatch):
    monkeypatch.setattr(constants, "now", lambda: _at(2))
    assert constants.daily_reset_boundary().day == 16
    assert constants.daily_reset_boundary().hour == 4


def test_reset_boundary_at_exactly_4am_is_today(monkeypatch):
    monkeypatch.setattr(constants, "now", lambda: _at(4, 0))
    assert constants.daily_reset_boundary() == _at(4, 0)
