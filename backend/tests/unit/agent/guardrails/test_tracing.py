from unittest.mock import MagicMock, patch

from agent.guardrails.tracing import set_guardrail_span_attributes


def _recording_span() -> MagicMock:
    span = MagicMock()
    span.is_recording.return_value = True
    return span


def test_sets_all_core_attributes():
    span = _recording_span()
    with patch("agent.guardrails.tracing.trace.get_current_span", return_value=span):
        set_guardrail_span_attributes(
            name="off_topic_guardrail",
            kind="input",
            passed=True,
            tripwire_triggered=False,
            reasoning="",
        )
    span.set_attribute.assert_any_call("guardrail.name", "off_topic_guardrail")
    span.set_attribute.assert_any_call("guardrail.kind", "input")
    span.set_attribute.assert_any_call("guardrail.passed", True)
    span.set_attribute.assert_any_call("guardrail.tripwire_triggered", False)


def test_sets_reasoning_when_present():
    span = _recording_span()
    with patch("agent.guardrails.tracing.trace.get_current_span", return_value=span):
        set_guardrail_span_attributes(
            name="prompt_injection_guardrail",
            kind="input",
            passed=False,
            tripwire_triggered=True,
            reasoning="injection attempt detected",
        )
    span.set_attribute.assert_any_call(
        "guardrail.reasoning", "injection attempt detected"
    )


def test_skips_reasoning_when_empty():
    span = _recording_span()
    with patch("agent.guardrails.tracing.trace.get_current_span", return_value=span):
        set_guardrail_span_attributes(
            name="message_length_guardrail",
            kind="input",
            passed=True,
            tripwire_triggered=False,
            reasoning="",
        )
    calls = [str(c) for c in span.set_attribute.call_args_list]
    assert not any("reasoning" in c for c in calls)


def test_no_op_when_span_not_recording():
    span = MagicMock()
    span.is_recording.return_value = False
    with patch("agent.guardrails.tracing.trace.get_current_span", return_value=span):
        set_guardrail_span_attributes(
            name="off_topic_guardrail",
            kind="input",
            passed=True,
            tripwire_triggered=False,
            reasoning="",
        )
    span.set_attribute.assert_not_called()
