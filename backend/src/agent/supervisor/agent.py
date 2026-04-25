from agents import Agent, ModelSettings

from agent.supervisor.instructions import get_intent_instructions
from llm.openai import get_openai_model


def create_supervisor_agent() -> Agent[None]:
    """Instantiate the supervisor agent that detects intent and routes to domain agents."""
    return Agent[None](
        name="Supervisor",
        handoff_description="Greets the customer, detects their intent, and routes to the appropriate domain agent.",
        instructions=get_intent_instructions,
        model=get_openai_model(),
        model_settings=ModelSettings(temperature=0.2, max_tokens=150),
    )
