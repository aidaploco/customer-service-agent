from __future__ import annotations

from agents import Agent, ModelSettings

from agent.general.instructions import get_general_instructions
from agent.general.tools import search_company_info
from agent.guardrails.message_length import message_length_guardrail
from agent.guardrails.off_topic import off_topic_guardrail
from agent.guardrails.prompt_injection import prompt_injection_guardrail
from llm.openai import get_openai_model


def create_general_agent(handoffs: list | None = None) -> Agent[None]:
    """Instantiate the general information agent."""
    return Agent[None](
        name="General",
        handoff_description="Handles general questions about Brightloop: company background, product features, pricing overview, security, compliance, and SLA.",
        instructions=get_general_instructions,
        model=get_openai_model(),
        model_settings=ModelSettings(temperature=0.2, max_tokens=512),
        tools=[search_company_info],
        input_guardrails=[
            message_length_guardrail,
            off_topic_guardrail,
            prompt_injection_guardrail,
        ],
        handoffs=handoffs or [],
    )
