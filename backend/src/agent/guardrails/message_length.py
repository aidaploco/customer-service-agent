from __future__ import annotations

from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, input_guardrail

from agent.guardrails import _last_user_message
from config import get_settings


@input_guardrail(run_in_parallel=False)
async def message_length_guardrail(
    _ctx: RunContextWrapper[None],
    _agent: Agent[None],
    input: str | list,
) -> GuardrailFunctionOutput:
    message = _last_user_message(input)
    if not message:
        return GuardrailFunctionOutput(output_info=None, tripwire_triggered=False)
    triggered = len(message) > get_settings().max_message_length
    return GuardrailFunctionOutput(output_info=None, tripwire_triggered=triggered)
