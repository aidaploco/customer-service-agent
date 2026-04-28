from unittest.mock import patch

import pytest

from agent.registry import build_agent_registry


@pytest.fixture
def registry(openai_env):
    with (
        patch("agent.supervisor.agent.get_openai_model", return_value=None),
        patch("agent.billing.agent.get_openai_model", return_value=None),
        patch("agent.support.agent.get_openai_model", return_value=None),
    ):
        return build_agent_registry()


def test_registry_contains_all_agents(registry):
    assert set(registry.keys()) == {"Supervisor", "Billing", "Support"}


def test_agent_names_match_keys(registry):
    for name, agent in registry.items():
        assert agent.name == name


def test_supervisor_routes_to_billing(registry):
    handoff_names = {h.name for h in registry["Supervisor"].handoffs}
    assert "Billing" in handoff_names


def test_supervisor_routes_to_support(registry):
    handoff_names = {h.name for h in registry["Supervisor"].handoffs}
    assert "Support" in handoff_names


def test_billing_returns_to_supervisor(registry):
    handoff_names = {h.name for h in registry["Billing"].handoffs}
    assert "Supervisor" in handoff_names


def test_support_returns_to_supervisor(registry):
    handoff_names = {h.name for h in registry["Support"].handoffs}
    assert "Supervisor" in handoff_names


def test_no_direct_billing_to_support_handoff(registry):
    handoff_names = {h.name for h in registry["Billing"].handoffs}
    assert "Support" not in handoff_names


def test_no_direct_support_to_billing_handoff(registry):
    handoff_names = {h.name for h in registry["Support"].handoffs}
    assert "Billing" not in handoff_names


def test_registry_returns_same_supervisor_instance(registry):
    """Back-handoffs must point to the same supervisor object, not a copy."""
    supervisor = registry["Supervisor"]
    billing_back = next(
        h for h in registry["Billing"].handoffs if h.name == "Supervisor"
    )
    support_back = next(
        h for h in registry["Support"].handoffs if h.name == "Supervisor"
    )
    assert billing_back is supervisor
    assert support_back is supervisor
