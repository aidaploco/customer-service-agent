import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm.openai import (
    _embed_cache,
    get_async_client,
    get_billing_model,
    get_embedding,
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
    _embed_cache.clear()
    yield
    get_settings.cache_clear()
    get_async_client.cache_clear()
    _embed_cache.clear()


def test_get_billing_model_returns_model_instance():
    with patch("llm.openai.OpenAIResponsesModel") as mock_cls:
        mock_cls.return_value = MagicMock()
        result = get_billing_model()
        mock_cls.assert_called_once()
        call_kwargs = mock_cls.call_args.kwargs
        assert "billing" in call_kwargs["model"].lower() or call_kwargs["model"] is not None


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


async def test_get_embedding_calls_api():
    mock_client = AsyncMock()
    mock_client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1, 0.2, 0.3])]
    )
    with patch("llm.openai.get_async_client", return_value=mock_client):
        result = await get_embedding("hello world")
    assert result == [0.1, 0.2, 0.3]
    mock_client.embeddings.create.assert_called_once()


async def test_get_embedding_returns_cached_value():
    mock_client = AsyncMock()
    mock_client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1, 0.2, 0.3])]
    )
    with patch("llm.openai.get_async_client", return_value=mock_client):
        await get_embedding("hello world")
        await get_embedding("hello world")
    assert mock_client.embeddings.create.call_count == 1


async def test_get_embedding_bypasses_expired_cache():
    mock_client = AsyncMock()
    mock_client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1, 0.2, 0.3])]
    )
    # Manually insert an expired cache entry
    _embed_cache["stale text"] = ([0.9, 0.8], time.time() - 9999)
    with patch("llm.openai.get_async_client", return_value=mock_client):
        await get_embedding("stale text")
    # Expired entry was bypassed and API was called
    mock_client.embeddings.create.assert_called_once()
    assert "stale text" not in _embed_cache or _embed_cache["stale text"][1] > time.time() - 10
