import time
from datetime import datetime, timezone

import openai
from agents import Agent, InputGuardrailTripwireTriggered, RunConfig, Runner
from agents.guardrail import InputGuardrailResult
from agents.items import HandoffOutputItem, RunItem, ToolCallItem, ToolCallOutputItem
from opentelemetry import trace

from agent.guardrails.message_length import message_length_guardrail
from agent.guardrails.off_topic import off_topic_guardrail
from agent.guardrails.prompt_injection import prompt_injection_guardrail
from agent.guardrails.responses import (
    log_all_passed,
    log_guardrail_trip,
    refusal_message,
)
from agent.registry import HANDOFF_INPUT_FILTER, build_agent_registry
from api.schemas.chat import AgentEvent, AgentInfo, ChatResponse, GuardrailResult
from store.base import BaseConversationStore
from utils.logger import get_logger

_logger = get_logger(__name__)
_tracer = trace.get_tracer(__name__)


def _agent_model_name(agent: Agent[None]) -> str:
    m = agent.model
    return m if isinstance(m, str) else getattr(m, "model", repr(m))


def _build_agents_lookup(registry: dict[str, Agent[None]]) -> dict[str, AgentInfo]:
    return {
        agent.name: AgentInfo(
            name=agent.name,
            description=agent.handoff_description or "",
            model=_agent_model_name(agent),
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

    def _api_error_response(self, session_id: str, message: str) -> ChatResponse:
        return ChatResponse(
            session_id=session_id,
            message=message,
            agent=self._agents_lookup["Supervisor"],
            guardrails=[],
            events=[],
        )

    async def process_message(self, session_id: str, message: str) -> ChatResponse:
        """Run the agent on the given message and return the response."""
        state = await self._store.get_or_create(session_id)

        starting_agent = (
            self._registry.get(state.current_agent_name) or self._registry["Supervisor"]
        )

        if state.messages:
            input_ = list(state.messages) + [{"role": "user", "content": message}]
        else:
            input_ = message

        start = time.perf_counter()
        with _tracer.start_as_current_span(
            "chat_session",
            attributes={
                "openinference.span.kind": "CHAIN",
                "input.value": message,
                "session.id": session_id,
            },
        ) as span:
            try:
                result = await Runner.run(
                    starting_agent=starting_agent,
                    input=input_,
                    run_config=RunConfig(
                        group_id=session_id,
                        handoff_input_filter=HANDOFF_INPUT_FILTER,
                        input_guardrails=[
                            message_length_guardrail,
                            prompt_injection_guardrail,
                            off_topic_guardrail,
                        ],
                    ),
                )
            except InputGuardrailTripwireTriggered as exc:
                gr = exc.guardrail_result
                refusal = refusal_message(gr.guardrail.get_name())
                span.set_attribute("output.value", refusal)
                log_guardrail_trip(_logger, session_id, gr)
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
            except openai.BadRequestError as exc:
                _logger.warning("session=%s bad_request: %s", session_id, exc)
                span.set_status(trace.StatusCode.ERROR, "bad_request")
                return self._api_error_response(
                    session_id,
                    "I wasn't able to process that request. Please try rephrasing.",
                )
            except openai.RateLimitError:
                _logger.warning("session=%s rate_limit_exceeded", session_id)
                span.set_status(trace.StatusCode.ERROR, "rate_limit")
                return self._api_error_response(
                    session_id,
                    "I'm experiencing high demand right now. Please try again in a moment.",
                )
            except openai.APIConnectionError:
                _logger.warning("session=%s connection_error", session_id)
                span.set_status(trace.StatusCode.ERROR, "connection_error")
                return self._api_error_response(
                    session_id,
                    "I'm having trouble connecting. Please try again in a moment.",
                )
            except openai.APIError as exc:
                _logger.error("session=%s api_error: %s", session_id, exc)
                span.set_status(trace.StatusCode.ERROR, "api_error")
                return self._api_error_response(
                    session_id,
                    "Something went wrong on my end. Please try again.",
                )
            reply = (
                result.final_output
                or "I'm sorry, I wasn't able to generate a response. Please try again."
            )
            span.set_attribute("output.value", reply)
        duration_ms = (time.perf_counter() - start) * 1000

        log_all_passed(_logger, session_id, result.input_guardrail_results)
        state.messages = result.to_input_list()
        state.current_agent_name = result.last_agent.name
        state.last_activity = datetime.now(timezone.utc)
        await self._store.save(state)

        _logger.info(
            "session=%s agent=%s duration=%.1fms",
            session_id,
            result.last_agent.name,
            duration_ms,
        )
        return ChatResponse(
            session_id=session_id,
            message=reply,
            agent=self._agents_lookup[result.last_agent.name],
            guardrails=_extract_triggered_guardrails(result.input_guardrail_results),
            events=_extract_events(result.new_items),
        )
