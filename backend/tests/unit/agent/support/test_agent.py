from unittest.mock import MagicMock, patch

import pytest

from agent.support.agent import create_support_agent


@pytest.fixture
def support(openai_env):
    with patch("agent.support.agent.get_openai_model", return_value=None):
        return create_support_agent()


def test_agent_name(support):
    assert support.name == "Support"


def test_agent_handoff_description(support):
    assert support.handoff_description is not None
    assert len(support.handoff_description) > 0


def test_agent_model_settings_temperature(support):
    assert support.model_settings.temperature == 0.2


def test_agent_model_settings_max_tokens(support):
    assert support.model_settings.max_tokens == 512


def test_agent_instructions_is_callable(support):
    assert callable(support.instructions)


def test_agent_has_tools(support):
    tool_names = {t.name for t in support.tools}
    assert tool_names == {
        "get_system_status",
        "search_knowledge_base",
        "create_ticket",
        "get_ticket_status",
    }


def test_agent_has_off_topic_guardrail(support):
    names = [g.get_name() for g in support.input_guardrails]
    assert "off_topic_guardrail" in names


def test_agent_has_injection_guardrail(support):
    names = [g.get_name() for g in support.input_guardrails]
    assert "prompt_injection_guardrail" in names


def test_agent_no_handoffs_by_default(support):
    assert support.handoffs == []


def test_agent_forwards_handoffs(openai_env):
    dummy = MagicMock()
    with patch("agent.support.agent.get_openai_model", return_value=None):
        agent = create_support_agent(handoffs=[dummy])
    assert dummy in agent.handoffs
