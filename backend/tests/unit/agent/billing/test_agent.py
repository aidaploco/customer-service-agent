from unittest.mock import MagicMock, patch

import pytest

from agent.billing.agent import create_billing_agent


@pytest.fixture
def billing(openai_env):
    with patch("agent.billing.agent.get_openai_model", return_value=None):
        return create_billing_agent()


def test_agent_name(billing):
    assert billing.name == "Billing"


def test_agent_handoff_description(billing):
    assert billing.handoff_description is not None
    assert len(billing.handoff_description) > 0


def test_agent_model_settings_temperature(billing):
    assert billing.model_settings.temperature == 0.2


def test_agent_model_settings_max_tokens(billing):
    assert billing.model_settings.max_tokens == 512


def test_agent_instructions_is_callable(billing):
    assert callable(billing.instructions)


def test_agent_no_handoffs_by_default(billing):
    assert billing.handoffs == []


def test_agent_forwards_handoffs(openai_env):
    dummy = MagicMock()
    with patch("agent.billing.agent.get_openai_model", return_value=None):
        agent = create_billing_agent(handoffs=[dummy])
    assert dummy in agent.handoffs
