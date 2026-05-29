# USD per 1M tokens. Verify current prices at https://openai.com/api/pricing/
_PRICES: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-5.4-mini-2026-03-17": {"input": 0.75, "output": 4.50},
}

_AGENT_CONFIG_KEY = {
    "Supervisor": "supervisor_model",
    "Billing": "billing_model",
    "Support": "support_model",
}


def estimate_cost_usd(
    last_agent: str,
    input_tokens: int,
    output_tokens: int,
    config: dict[str, str],
) -> float | None:
    """Return estimated USD cost for one eval case, or None if model price is unknown."""
    config_key = _AGENT_CONFIG_KEY.get(last_agent)
    if not config_key:
        return None
    model = config.get(config_key)
    if not model:
        return None
    prices = _PRICES.get(model)
    if not prices:
        return None
    return (
        input_tokens * prices["input"] + output_tokens * prices["output"]
    ) / 1_000_000
