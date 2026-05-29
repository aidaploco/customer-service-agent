from __future__ import annotations

from agents import Agent, ModelSettings

from agent.support.instructions import get_support_instructions
from agent.support.tools import (
    create_ticket,
    get_system_status,
    get_ticket_status,
    search_knowledge_base,
)
from llm.openai import get_support_model


def create_support_agent(handoffs: list | None = None) -> Agent[None]:
    """Instantiate the support agent (technical support + general company questions)."""
    return Agent[None](
        name="Support",
        handoff_description="Handles technical issues, product questions, company information, pricing, security, compliance, SLA, and anything not related to billing.",
        instructions=get_support_instructions,
        model=get_support_model(),
        model_settings=ModelSettings(temperature=0.1, max_tokens=800),
        tools=[
            get_system_status,
            search_knowledge_base,
            create_ticket,
            get_ticket_status,
        ],
        handoffs=handoffs or [],
    )
