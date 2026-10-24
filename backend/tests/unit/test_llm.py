from unittest.mock import MagicMock, patch

import pytest

from llm.openai import (
    get_async_client,
    get_billing_model,
    get_guardrail_model,
    get_supervisor_model,
    get_support_model,
)


@pytest.fixture(autouse=True)
def clear_llm_state(monkeypatch):
    from config import get_settings

    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    get_settings.cache_clear()
    get_async_client.cache_clear()
    yield
    get_settings.cache_clear()
    get_async_client.cache_clear()


def test_get_billing_model_returns_model_instance():
    with patch("llm.openai.OpenAIResponsesModel") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_billing_model()
        mock_cls.assert_called_once()


def test_get_support_model_returns_model_instance():
    with patch("llm.openai.OpenAIResponsesModel") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_support_model()
        mock_cls.assert_called_once()


def test_get_supervisor_model_returns_model_instance():
    with patch("llm.openai.OpenAIResponsesModel") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_supervisor_model()
        mock_cls.assert_called_once()


def test_get_guardrail_model_returns_model_instance():
    with patch("llm.openai.OpenAIResponsesModel") as mock_cls:
        mock_cls.return_value = MagicMock()
        get_guardrail_model()
        mock_cls.assert_called_once()
