from __future__ import annotations

from agents import Agent, ModelSettings

from agent.supervisor.instructions import get_intent_instructions
from llm.openai import get_supervisor_model


def create_supervisor_agent(handoffs: list | None = None) -> Agent[None]:
    """Instantiate the supervisor agent that detects intent and routes to domain agents."""
    return Agent[None](
        name="Supervisor",
        handoff_description="Detects customer intent and routes to the appropriate domain agent.",
        instructions=get_intent_instructions,
        model=get_supervisor_model(),
        model_settings=ModelSettings(temperature=0.1, max_tokens=150),
        tool_use_behavior="stop_on_first_tool",
        handoffs=handoffs or [],
    )
