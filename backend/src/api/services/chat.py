import time
from datetime import datetime, timezone

from agents import Agent, InputGuardrailTripwireTriggered, Runner
from agents.guardrail import InputGuardrailResult
from agents.items import HandoffOutputItem, RunItem, ToolCallItem, ToolCallOutputItem

from agent.guardrails.responses import (
    log_all_passed,
    log_guardrail_trip,
    refusal_message,
)
from agent.registry import build_agent_registry
from api.schemas.chat import AgentEvent, AgentInfo, ChatResponse, GuardrailResult
from store.base import BaseConversationStore
from utils.logger import get_logger

logger = get_logger(__name__)


def _build_agents_lookup(registry: dict[str, Agent[None]]) -> dict[str, AgentInfo]:
    return {
        agent.name: AgentInfo(
            name=agent.name,
            description=agent.handoff_description or "",
            tools=[t.name for t in agent.tools if hasattr(t, "name")],
            handoffs=[h.name for h in agent.handoffs],
        )
        for agent in registry.values()
    }


def _extract_events(new_items: list[RunItem]) -> list[AgentEvent]:
    events = []
    for item in new_items:
        if isinstance(item, HandoffOutputItem):
            events.append(
                AgentEvent(
                    type="handoff",
                    agent=item.source_agent.name,
                    content=item.target_agent.name,
                )
            )
        elif isinstance(item, ToolCallItem):
            name = getattr(item.raw_item, "name", None) or "unknown"
            args = getattr(item.raw_item, "arguments", "") or ""
            events.append(
                AgentEvent(
                    type="tool_call",
                    agent=item.agent.name,
                    content=f"{name}({args})",
                )
            )
        elif isinstance(item, ToolCallOutputItem):
            events.append(
                AgentEvent(
                    type="tool_output",
                    agent=item.agent.name,
                    content=str(item.output)[:500],
                )
            )
    return events


def _extract_triggered_guardrails(
    guardrail_results: list[InputGuardrailResult],
) -> list[GuardrailResult]:
    return [
        GuardrailResult(
            name=gr.guardrail.get_name(),
            passed=False,
            reasoning=getattr(gr.output.output_info, "reason", None),
        )
        for gr in guardrail_results
        if gr.output.tripwire_triggered
    ]


class ChatService:
    """Orchestrates agent execution for a single chat turn."""

    def __init__(self, store: BaseConversationStore) -> None:
        self._registry = build_agent_registry()
        self._store = store
        self._agents_lookup = _build_agents_lookup(self._registry)

    @property
    def agents(self) -> list[AgentInfo]:
        return list(self._agents_lookup.values())

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
                session_id=session_id,
                message=refusal,
                agent=self._agents_lookup["Supervisor"],
                guardrails=_extract_triggered_guardrails([gr]),
                events=[],
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
            agent=self._agents_lookup[result.last_agent.name],
            guardrails=_extract_triggered_guardrails(result.input_guardrail_results),
            events=_extract_events(result.new_items),
        )
