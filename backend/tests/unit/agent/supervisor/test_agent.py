from unittest.mock import patch

import pytest

from agent.supervisor.agent import create_supervisor_agent


@pytest.fixture
def supervisor(openai_env):
    """Create a supervisor agent with a mocked model."""
    with patch("agent.supervisor.agent.get_supervisor_model", return_value=None):
        return create_supervisor_agent()


def test_agent_name(supervisor):
    assert supervisor.name == "Supervisor"


def test_agent_handoff_description(supervisor):
    assert supervisor.handoff_description is not None
    assert len(supervisor.handoff_description) > 0


def test_agent_model_settings_temperature(supervisor):
    assert supervisor.model_settings.temperature == 0.1


def test_agent_model_settings_max_tokens(supervisor):
    assert supervisor.model_settings.max_tokens == 150


def test_agent_instructions_is_callable(supervisor):
    assert callable(supervisor.instructions)


def test_agent_has_no_tools(supervisor):
    assert supervisor.tools == []


def test_agent_tool_choice_required(supervisor):
    assert supervisor.model_settings.tool_choice == "required"


def test_agent_tool_use_behavior(supervisor):
    assert supervisor.tool_use_behavior == "stop_on_first_tool"
