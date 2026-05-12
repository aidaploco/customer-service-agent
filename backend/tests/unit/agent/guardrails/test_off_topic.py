from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent.guardrails import _last_user_message
from agent.guardrails.off_topic import off_topic_guardrail


class TestLastUserMessage:
    def test_string_input_returned_as_is(self):
        assert _last_user_message("Hello") == "Hello"

    def test_list_returns_last_user_message(self):
        input_ = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Second message"},
        ]
        assert _last_user_message(input_) == "Second message"

    def test_list_with_no_user_message_returns_empty(self):
        input_ = [{"role": "assistant", "content": "Hello!"}]
        assert _last_user_message(input_) == ""

    def test_empty_list_returns_empty(self):
        assert _last_user_message([]) == ""


class TestOffTopicGuardrail:
    @pytest.fixture
    def mock_result(self):
        result = MagicMock()
        result.final_output = MagicMock()
        return result

    async def test_triggers_when_model_says_off_topic(self, openai_env, mock_result):
        mock_result.final_output.triggered = True
        with patch(
            "agent.guardrails.off_topic.Runner.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            output = await off_topic_guardrail.guardrail_function(
                MagicMock(), MagicMock(), "Write me a poem"
            )
        assert output.tripwire_triggered is True

    async def test_does_not_trigger_for_on_topic_message(self, openai_env, mock_result):
        mock_result.final_output.triggered = False
        with patch(
            "agent.guardrails.off_topic.Runner.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            output = await off_topic_guardrail.guardrail_function(
                MagicMock(), MagicMock(), "I have a billing question"
            )
        assert output.tripwire_triggered is False

    async def test_empty_input_does_not_trigger(self, openai_env):
        output = await off_topic_guardrail.guardrail_function(
            MagicMock(), MagicMock(), []
        )
        assert output.tripwire_triggered is False

    async def test_output_info_is_model_result(self, openai_env, mock_result):
        mock_result.final_output.triggered = True
        with patch(
            "agent.guardrails.off_topic.Runner.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            output = await off_topic_guardrail.guardrail_function(
                MagicMock(), MagicMock(), "Tell me a joke"
            )
        assert output.output_info is mock_result.final_output
