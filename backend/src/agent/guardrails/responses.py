from __future__ import annotations

import logging

from agents import InputGuardrailResult

_REFUSAL_MESSAGES: dict[str, str] = {
    "off_topic_guardrail": (
        "I can only help with Brightloop billing and support topics. "
        "Is there anything along those lines I can assist you with?"
    ),
    "prompt_injection_guardrail": "I'm not able to process that request.",
}
_FALLBACK_REFUSAL = "I'm not able to process that request."


def refusal_message(guardrail_name: str) -> str:
    """Return the appropriate refusal text for a triggered guardrail."""
    return _REFUSAL_MESSAGES.get(guardrail_name, _FALLBACK_REFUSAL)


def log_guardrail_trip(
    logger: logging.Logger,
    session_id: str,
    guardrail_result: InputGuardrailResult,
) -> None:
    """Log a guardrail trip at WARNING, including the classifier's reason when available."""
    reason = getattr(
        guardrail_result.output.output_info, "reason", "no reason provided"
    )
    logger.warning(
        "session=%s guardrail=%s TRIPPED reason=%r",
        session_id,
        guardrail_result.guardrail.get_name(),
        reason,
    )


def log_all_passed(
    logger: logging.Logger,
    session_id: str,
    results: list[InputGuardrailResult],
) -> None:
    """Log each guardrail result at DEBUG when all passed."""
    for result in results:
        reason = getattr(result.output.output_info, "reason", "-")
        logger.debug(
            "session=%s guardrail=%s passed reason=%r",
            session_id,
            result.guardrail.get_name(),
            reason,
        )
