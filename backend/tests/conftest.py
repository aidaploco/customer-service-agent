import pytest

from config import get_settings
from llm.openai import get_async_client


@pytest.fixture(autouse=True)
def clear_caches():
    """Clear all lru_cache singletons between tests to prevent state leaking."""
    get_settings.cache_clear()
    get_async_client.cache_clear()
    yield
    get_settings.cache_clear()
    get_async_client.cache_clear()


@pytest.fixture
def openai_env(monkeypatch):
    """Inject dummy OpenAI credentials so Settings validation passes."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
