import pytest

from evals.pricing import estimate_cost_usd


def test_known_supervisor_model():
    cfg = {"supervisor_model": "gpt-4o-mini"}
    result = estimate_cost_usd("Supervisor", 1_000_000, 1_000_000, cfg)
    expected = (1_000_000 * 0.15 + 1_000_000 * 0.60) / 1_000_000
    assert result == pytest.approx(expected)


def test_known_billing_model():
    cfg = {"billing_model": "gpt-4o"}
    result = estimate_cost_usd("Billing", 1_000_000, 1_000_000, cfg)
    expected = (1_000_000 * 2.50 + 1_000_000 * 10.00) / 1_000_000
    assert result == pytest.approx(expected)


def test_known_support_model():
    cfg = {"support_model": "gpt-5.4-mini-2026-03-17"}
    result = estimate_cost_usd("Support", 500_000, 200_000, cfg)
    expected = (500_000 * 0.75 + 200_000 * 4.50) / 1_000_000
    assert result == pytest.approx(expected)


def test_unknown_agent_returns_none():
    cfg = {"supervisor_model": "gpt-4o-mini"}
    assert estimate_cost_usd("General", 100, 50, cfg) is None


def test_missing_config_key_returns_none():
    assert estimate_cost_usd("Supervisor", 100, 50, {}) is None


def test_unknown_model_returns_none():
    cfg = {"supervisor_model": "gpt-99-ultra"}
    assert estimate_cost_usd("Supervisor", 100, 50, cfg) is None


def test_zero_tokens_returns_zero():
    cfg = {"billing_model": "gpt-4o-mini"}
    result = estimate_cost_usd("Billing", 0, 0, cfg)
    assert result == pytest.approx(0.0)
