from unittest.mock import MagicMock

from agent.support.instructions import get_support_instructions


def _call() -> str:
    return get_support_instructions(MagicMock(), MagicMock())


def test_returns_string():
    assert isinstance(_call(), str)


def test_no_leading_or_trailing_whitespace():
    result = _call()
    assert result == result.strip()


def test_contains_persona():
    result = _call()
    assert "Zara" in result
    assert "Brightloop" in result


def test_covers_support_topics():
    result = _call()
    assert "bug" in result.lower()
    assert "api" in result.lower()
    assert "integration" in result.lower()


def test_ticket_reference_format_documented():
    result = _call()
    assert "BL-" in result


def test_handoff_is_invisible_to_user():
    result = " ".join(_call().split())  # collapse newlines before asserting
    assert "silently" in result.lower()
    assert "do not mention" in result.lower()
