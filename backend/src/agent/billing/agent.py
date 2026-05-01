from __future__ import annotations

from agents import Agent, ModelSettings

from agent.billing.instructions import get_billing_instructions
from agent.billing.tools import (
    cancel_subscription,
    get_invoice_history,
    get_subscription,
    request_refund,
    update_plan,
)
from llm.openai import get_openai_model


def create_billing_agent(handoffs: list | None = None) -> Agent[None]:
    """Instantiate the billing specialist agent."""
    return Agent[None](
        name="Billing",
        handoff_description="Handles subscription plans, invoices, payments, upgrades, cancellations, and billing disputes.",
        instructions=get_billing_instructions,
        model=get_openai_model(),
        model_settings=ModelSettings(temperature=0.2, max_tokens=512),
        tools=[
            get_subscription,
            get_invoice_history,
            update_plan,
            request_refund,
            cancel_subscription,
        ],
        handoffs=handoffs or [],
    )
