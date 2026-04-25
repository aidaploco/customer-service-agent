from unittest.mock import MagicMock

from agent.supervisor.instructions import get_intent_instructions


def _call() -> str:
    """Invoke with mock ctx/agent — the function doesn't use them."""
    return get_intent_instructions(MagicMock(), MagicMock())


def test_returns_string():
    assert isinstance(_call(), str)


def test_no_leading_or_trailing_whitespace():
    result = _call()
    assert result == result.strip()


def test_contains_persona():
    result = _call()
    assert "Zara" in result
    assert "Brightloop" in result
