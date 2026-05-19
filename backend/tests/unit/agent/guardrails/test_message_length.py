from unittest.mock import MagicMock, patch

from agent.guardrails.message_length import message_length_guardrail


class TestMessageLengthGuardrail:
    async def test_short_message_does_not_trigger(self, openai_env):
        output = await message_length_guardrail.guardrail_function(
            MagicMock(), MagicMock(), "Hi, I need help with my invoice."
        )
        assert output.tripwire_triggered is False

    async def test_message_at_limit_does_not_trigger(self, openai_env):
        with patch("agent.guardrails.message_length.get_settings") as mock_settings:
            mock_settings.return_value.max_message_length = 10
            output = await message_length_guardrail.guardrail_function(
                MagicMock(), MagicMock(), "a" * 10
            )
        assert output.tripwire_triggered is False

    async def test_message_one_over_limit_triggers(self, openai_env):
        with patch("agent.guardrails.message_length.get_settings") as mock_settings:
            mock_settings.return_value.max_message_length = 10
            output = await message_length_guardrail.guardrail_function(
                MagicMock(), MagicMock(), "a" * 11
            )
        assert output.tripwire_triggered is True

    async def test_empty_input_does_not_trigger(self, openai_env):
        output = await message_length_guardrail.guardrail_function(
            MagicMock(), MagicMock(), []
        )
        assert output.tripwire_triggered is False

    async def test_list_input_checks_last_user_message(self, openai_env):
        with patch("agent.guardrails.message_length.get_settings") as mock_settings:
            mock_settings.return_value.max_message_length = 10
            input_ = [
                {"role": "user", "content": "short"},
                {"role": "assistant", "content": "response"},
                {"role": "user", "content": "a" * 11},
            ]
            output = await message_length_guardrail.guardrail_function(
                MagicMock(), MagicMock(), input_
            )
        assert output.tripwire_triggered is True

    async def test_output_info_is_none(self, openai_env):
        with patch("agent.guardrails.message_length.get_settings") as mock_settings:
            mock_settings.return_value.max_message_length = 10
            output = await message_length_guardrail.guardrail_function(
                MagicMock(), MagicMock(), "a" * 11
            )
        assert output.output_info is None
