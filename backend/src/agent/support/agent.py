from __future__ import annotations

from agents import Agent, ModelSettings

from agent.guardrails.off_topic import off_topic_guardrail
from agent.guardrails.prompt_injection import prompt_injection_guardrail
from agent.support.instructions import get_support_instructions
from agent.support.tools import (
    create_ticket,
    get_system_status,
    get_ticket_status,
    search_knowledge_base,
)
from llm.openai import get_openai_model


def create_support_agent(handoffs: list | None = None) -> Agent[None]:
    """Instantiate the technical support specialist agent."""
    return Agent[None](
        name="Support",
        handoff_description="Handles bug reports, API questions, integrations, performance issues, and general technical problems.",
        instructions=get_support_instructions,
        model=get_openai_model(),
        model_settings=ModelSettings(temperature=0.2, max_tokens=512),
        tools=[
            get_system_status,
            search_knowledge_base,
            create_ticket,
            get_ticket_status,
        ],
        input_guardrails=[off_topic_guardrail, prompt_injection_guardrail],
        handoffs=handoffs or [],
    )
