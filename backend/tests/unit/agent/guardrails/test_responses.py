import logging
from unittest.mock import MagicMock

from agent.guardrails.responses import (
    _FALLBACK_REFUSAL,
    log_all_passed,
    log_guardrail_trip,
    refusal_message,
)


class TestRefusalMessage:
    def test_known_off_topic_guardrail(self):
        msg = refusal_message("off_topic_guardrail")
        assert "brightloop" in msg.lower()

    def test_known_injection_guardrail(self):
        msg = refusal_message("prompt_injection_guardrail")
        assert "not able" in msg.lower()

    def test_unknown_guardrail_returns_fallback(self):
        assert refusal_message("unknown_guardrail") == _FALLBACK_REFUSAL


class TestLogGuardrailTrip:
    def _make_result(
        self, name: str, reason: str | None = "it was off topic"
    ) -> MagicMock:
        result = MagicMock()
        result.guardrail.get_name.return_value = name
        result.output.output_info = (
            MagicMock(reason=reason) if reason is not None else None
        )
        return result

    def test_logs_at_warning_level(self, caplog):
        result = self._make_result("off_topic_guardrail")
        with caplog.at_level(logging.WARNING):
            log_guardrail_trip(logging.getLogger("test"), "s1", result)
        assert any(r.levelno == logging.WARNING for r in caplog.records)

    def test_includes_guardrail_name(self, caplog):
        result = self._make_result("prompt_injection_guardrail")
        with caplog.at_level(logging.WARNING):
            log_guardrail_trip(logging.getLogger("test"), "s1", result)
        assert "prompt_injection_guardrail" in caplog.text

    def test_includes_session_id(self, caplog):
        result = self._make_result("off_topic_guardrail")
        with caplog.at_level(logging.WARNING):
            log_guardrail_trip(logging.getLogger("test"), "session-abc", result)
        assert "session-abc" in caplog.text

    def test_includes_reason(self, caplog):
        result = self._make_result(
            "off_topic_guardrail", reason="customer asked for a poem"
        )
        with caplog.at_level(logging.WARNING):
            log_guardrail_trip(logging.getLogger("test"), "s1", result)
        assert "customer asked for a poem" in caplog.text

    def test_handles_missing_reason(self, caplog):
        result = self._make_result("off_topic_guardrail", reason=None)
        with caplog.at_level(logging.WARNING):
            log_guardrail_trip(logging.getLogger("test"), "s1", result)
        assert "no reason provided" in caplog.text


class TestLogAllPassed:
    def _make_result(self, name: str, reason: str = "on topic") -> MagicMock:
        result = MagicMock()
        result.guardrail.get_name.return_value = name
        result.output.output_info = MagicMock(reason=reason)
        return result

    def test_logs_at_debug_level(self, caplog):
        results = [self._make_result("off_topic_guardrail")]
        with caplog.at_level(logging.DEBUG):
            log_all_passed(logging.getLogger("test"), "s1", results)
        assert any(r.levelno == logging.DEBUG for r in caplog.records)

    def test_logs_each_guardrail(self, caplog):
        results = [
            self._make_result("off_topic_guardrail"),
            self._make_result("prompt_injection_guardrail"),
        ]
        with caplog.at_level(logging.DEBUG):
            log_all_passed(logging.getLogger("test"), "s1", results)
        assert "off_topic_guardrail" in caplog.text
        assert "prompt_injection_guardrail" in caplog.text

    def test_empty_results_logs_nothing(self, caplog):
        with caplog.at_level(logging.DEBUG):
            log_all_passed(logging.getLogger("test"), "s1", [])
        assert caplog.records == []
