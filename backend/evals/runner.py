import time
from functools import lru_cache

from agents import InputGuardrailTripwireTriggered, RunConfig, Runner
from agents.items import HandoffOutputItem, ToolCallItem

from agent.guardrails.message_length import message_length_guardrail
from agent.guardrails.off_topic import off_topic_guardrail
from agent.guardrails.prompt_injection import prompt_injection_guardrail
from agent.registry import build_agent_registry
from evals.models import EvalCase, ExecutionSummary


@lru_cache(maxsize=1)
def _registry():
    return build_agent_registry()


async def run_case(case: EvalCase) -> ExecutionSummary:
    registry = _registry()
    supervisor = registry["Supervisor"]

    input_ = case.messages if len(case.messages) > 1 else case.messages[0]["content"]

    start = time.perf_counter()
    try:
        result = await Runner.run(
            starting_agent=supervisor,
            input=input_,
            run_config=RunConfig(
                input_guardrails=[
                    message_length_guardrail,
                    prompt_injection_guardrail,
                    off_topic_guardrail,
                ],
            ),
        )
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

    return ExecutionSummary(
        case_id=case.id,
        final_output=result.final_output or "",
        last_agent=result.last_agent.name,
        handoff_chain=handoff_chain,
        tool_calls=tool_calls,
        triggered_guardrails=triggered_guardrails,
        latency_ms=latency_ms,
    )
