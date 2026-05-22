from __future__ import annotations

from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, input_guardrail

from agent.guardrails import _last_user_message
from agent.guardrails.tracing import set_guardrail_span_attributes
from config import get_settings


@input_guardrail
async def message_length_guardrail(
    _ctx: RunContextWrapper[None],
    _agent: Agent[None],
    input: str | list,
) -> GuardrailFunctionOutput:
    message = _last_user_message(input)
    triggered = bool(message) and len(message) > get_settings().max_message_length
    set_guardrail_span_attributes(
        name="message_length_guardrail",
        kind="input",
        passed=not triggered,
        tripwire_triggered=triggered,
        reasoning="",
    )
    return GuardrailFunctionOutput(output_info=None, tripwire_triggered=triggered)
