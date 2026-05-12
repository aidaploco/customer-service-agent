import time
from datetime import datetime, timezone

from agents import InputGuardrailTripwireTriggered, Runner

from agent.guardrails.responses import (
    log_all_passed,
    log_guardrail_trip,
    refusal_message,
)
from agent.registry import build_agent_registry
from api.schemas.chat import ChatResponse
from store.base import BaseConversationStore
from utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """Orchestrates agent execution for a single chat turn."""

    def __init__(self, store: BaseConversationStore) -> None:
        self._registry = build_agent_registry()
        self._store = store

    async def process_message(self, session_id: str, message: str) -> ChatResponse:
        """Run the agent on the given message and return the response."""
        state = await self._store.get_or_create(session_id)

        starting_agent = self._registry.get(state.current_agent_name)
        if starting_agent is None:
            starting_agent = self._registry["Supervisor"]

        if state.messages:
            input_ = state.messages + [{"role": "user", "content": message}]
        else:
            input_ = message

        start = time.perf_counter()
        try:
            result = await Runner.run(starting_agent=starting_agent, input=input_)
        except InputGuardrailTripwireTriggered as exc:
            gr = exc.guardrail_result
            refusal = refusal_message(gr.guardrail.get_name())
            log_guardrail_trip(logger, session_id, gr)
            state.messages = list(state.messages) + [
                {"role": "user", "content": message},
                {"role": "assistant", "content": refusal},
            ]
            state.last_activity = datetime.now(timezone.utc)
            await self._store.save(state)
            return ChatResponse(
                session_id=session_id, message=refusal, agent="Supervisor"
            )
        duration_ms = (time.perf_counter() - start) * 1000

        log_all_passed(logger, session_id, result.input_guardrail_results)
        state.messages = result.to_input_list()
        state.current_agent_name = result.last_agent.name
        state.last_activity = datetime.now(timezone.utc)
        await self._store.save(state)

        logger.info(
            "session=%s agent=%s duration=%.1fms",
            session_id,
            result.last_agent.name,
            duration_ms,
        )
        return ChatResponse(
            session_id=session_id,
            message=result.final_output,
            agent=result.last_agent.name,
        )
