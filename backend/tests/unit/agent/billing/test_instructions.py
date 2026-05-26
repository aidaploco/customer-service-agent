from unittest.mock import MagicMock

from agent.billing.instructions import get_billing_instructions


def _call() -> str:
    return get_billing_instructions(MagicMock(), MagicMock())


def test_returns_string():
    assert isinstance(_call(), str)


def test_no_leading_or_trailing_whitespace():
    result = _call()
    assert result == result.strip()


def test_contains_persona():
    result = _call()
    assert "Zara" in result
    assert "Brightloop" in result


def test_covers_billing_topics():
    result = _call()
    assert "invoice" in result.lower()
    assert "subscription" in result.lower()
    assert "payment" in result.lower()


def test_handoff_is_invisible_to_user():
    result = " ".join(_call().split())  # collapse newlines before asserting
    assert "handoff tool" in result.lower()
    assert "does not exist" in result.lower()  # routing is invisible by principle, not forbidden-phrase list
