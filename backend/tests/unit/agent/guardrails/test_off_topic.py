from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent.guardrails import _conversation_context, _last_user_message
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


class TestConversationContext:
    def test_string_input_returns_empty_context_and_message(self):
        ctx, msg = _conversation_context("Hello")
        assert ctx == ""
        assert msg == "Hello"

    def test_empty_list_returns_empty_strings(self):
        ctx, msg = _conversation_context([])
        assert ctx == ""
        assert msg == ""

    def test_extracts_last_user_message(self):
        input_ = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Second"},
        ]
        ctx, msg = _conversation_context(input_)
        assert msg == "Second"

    def test_conversation_includes_recent_turns(self):
        input_ = [
            {"role": "user", "content": "Can I upgrade my plan?"},
            {"role": "assistant", "content": "Which plan would you like?"},
            {"role": "user", "content": "business"},
        ]
        ctx, msg = _conversation_context(input_)
        assert msg == "business"
        assert "Can I upgrade my plan?" in ctx
        assert "Which plan would you like?" in ctx
        assert "business" in ctx

    def test_respects_max_turns(self):
        input_ = [{"role": "user", "content": f"msg{i}"} for i in range(20)]
        ctx, _ = _conversation_context(input_, max_turns=2)
        assert "msg0" not in ctx

    def test_skips_non_string_content(self):
        input_ = [
            {"role": "user", "content": [{"type": "text", "text": "complex"}]},
            {"role": "user", "content": "plain"},
        ]
        _, msg = _conversation_context(input_)
        assert msg == "plain"


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

    async def test_contextual_reply_includes_conversation_in_prompt(
        self, openai_env, mock_result
    ):
        """Short follow-up replies must be evaluated with conversation history, not in isolation."""
        mock_result.final_output.triggered = False
        input_ = [
            {"role": "user", "content": "I want to upgrade my plan"},
            {
                "role": "assistant",
                "content": "Sure! We have Starter, Business, or Enterprise. Which do you want?",
            },
            {"role": "user", "content": "business"},
        ]
        with patch(
            "agent.guardrails.off_topic.Runner.run",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_run:
            await off_topic_guardrail.guardrail_function(
                MagicMock(), MagicMock(), input_
            )
        _, call_kwargs = mock_run.call_args
        prompt = call_kwargs["input"]
        assert "<conversation>" in prompt
        assert "Which do you want?" in prompt
        assert "<msg>business</msg>" in prompt
