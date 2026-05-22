from unittest.mock import MagicMock, patch

import pytest

from agent.general.agent import create_general_agent


@pytest.fixture
def general(openai_env):
    with patch("agent.general.agent.get_domain_model", return_value=None):
        return create_general_agent()


def test_agent_name(general):
    assert general.name == "General"


def test_agent_handoff_description(general):
    assert general.handoff_description is not None
    assert len(general.handoff_description) > 0


def test_agent_model_settings_temperature(general):
    assert general.model_settings.temperature == 0.2


def test_agent_model_settings_max_tokens(general):
    assert general.model_settings.max_tokens == 400


def test_agent_instructions_is_callable(general):
    assert callable(general.instructions)


def test_agent_has_tools(general):
    tool_names = {t.name for t in general.tools}
    assert tool_names == {"search_company_info"}


def test_agent_no_handoffs_by_default(general):
    assert general.handoffs == []


def test_agent_forwards_handoffs(openai_env):
    dummy = MagicMock()
    with patch("agent.general.agent.get_domain_model", return_value=None):
        agent = create_general_agent(handoffs=[dummy])
    assert dummy in agent.handoffs
