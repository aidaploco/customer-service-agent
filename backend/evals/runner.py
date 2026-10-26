import asyncio
import time
from functools import lru_cache

import openai
from agents import InputGuardrailTripwireTriggered, RunConfig, Runner
from agents.items import HandoffOutputItem, ToolCallItem

from agent.guardrails.message_length import message_length_guardrail
from agent.guardrails.off_topic import off_topic_guardrail
from agent.guardrails.prompt_injection import prompt_injection_guardrail
from agent.registry import HANDOFF_INPUT_FILTER, build_agent_registry
from evals.models import EvalCase, ExecutionSummary


@lru_cache(maxsize=1)
def _registry():
    return build_agent_registry()


async def run_case(case: EvalCase) -> ExecutionSummary:
    registry = _registry()
    starting_agent = registry[case.start_agent]

    input_ = case.messages if len(case.messages) > 1 else case.messages[0]["content"]

    start = time.perf_counter()
    try:
        last_rate_limit_exc: Exception | None = None
        for attempt in range(3):
            try:
                result = await Runner.run(
                    starting_agent=starting_agent,
                    input=input_,
                    run_config=RunConfig(
                        handoff_input_filter=HANDOFF_INPUT_FILTER,
                        input_guardrails=[
                            message_length_guardrail,
                            prompt_injection_guardrail,
                            off_topic_guardrail,
                        ],
                    ),
                )
                break
            except openai.RateLimitError as exc:
                last_rate_limit_exc = exc
                if attempt < 2:
                    await asyncio.sleep(10 * (attempt + 1))
        else:
            raise last_rate_limit_exc  # type: ignore[misc]
    except InputGuardrailTripwireTriggered as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        gr = exc.guardrail_result
        return ExecutionSummary(
            case_id=case.id,
            final_output="",
            last_agent="Supervisor",
            handoff_chain=[],
            tool_calls=[],
            triggered_guardrails=[gr.guardrail.get_name()],
            latency_ms=latency_ms,
        )
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        return ExecutionSummary(
            case_id=case.id,
            final_output="",
            last_agent="",
            handoff_chain=[],
            tool_calls=[],
            triggered_guardrails=[],
            latency_ms=latency_ms,
            error=str(exc),
        )

    latency_ms = (time.perf_counter() - start) * 1000

    handoff_chain = [
        item.target_agent.name
        for item in result.new_items
        if isinstance(item, HandoffOutputItem)
    ]

    tool_calls = [
        (item.agent.name, getattr(item.raw_item, "name", "unknown"))
        for item in result.new_items
        if isinstance(item, ToolCallItem)
    ]

    triggered_guardrails = [
        gr.guardrail.get_name()
        for gr in result.input_guardrail_results
        if gr.output.tripwire_triggered
    ]

    input_tokens = sum(r.usage.input_tokens for r in result.raw_responses)
    output_tokens = sum(r.usage.output_tokens for r in result.raw_responses)

    return ExecutionSummary(
        case_id=case.id,
        final_output=result.final_output or "",
        last_agent=result.last_agent.name,
        handoff_chain=handoff_chain,
        tool_calls=tool_calls,
        triggered_guardrails=triggered_guardrails,
        latency_ms=latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
