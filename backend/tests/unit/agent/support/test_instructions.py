from unittest.mock import MagicMock

from agent.support.instructions import _KNOWLEDGE_DIR, get_support_instructions


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
    assert "handoff tool" in result.lower()
    assert (
        "does not exist" in result.lower()
    )  # routing is invisible by principle, not forbidden-phrase list


def test_includes_every_knowledge_document():
    """Each knowledge file is loaded verbatim into the prompt."""
    result = _call()
    for path in sorted(_KNOWLEDGE_DIR.glob("*.md")):
        assert path.read_text().strip() in result


def test_knowledge_lists_all_four_plans():
    """Pricing knowledge must match the plans the billing service offers."""
    from services.billing.mock_data import PLANS

    result = _call()
    for plan in PLANS:
        assert plan in result


def test_knowledge_placeholder_is_replaced():
    assert "{{KNOWLEDGE}}" not in _call()
