from opentelemetry import trace


def set_guardrail_span_attributes(
    *,
    name: str,
    kind: str,
    passed: bool,
    tripwire_triggered: bool,
    reasoning: str,
) -> None:
    span = trace.get_current_span()
    if not span.is_recording():
        return
    span.set_attribute("guardrail.name", name)
    span.set_attribute("guardrail.kind", kind)
    span.set_attribute("guardrail.passed", passed)
    span.set_attribute("guardrail.tripwire_triggered", tripwire_triggered)
    if reasoning:
        span.set_attribute("guardrail.reasoning", reasoning)
