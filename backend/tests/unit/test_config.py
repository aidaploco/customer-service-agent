import pytest
from pydantic import ValidationError

from config import Settings


def test_missing_api_key_raises():
    """Settings must fail fast when OPENAI_API_KEY is absent."""
    with pytest.raises(ValidationError):
        Settings(openai_api_key=None)


def test_default_values(monkeypatch):
    """Confirm defaults match expected values, ignoring any local .env or env vars."""
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("API_PREFIX", raising=False)
    settings = Settings(_env_file=None, openai_api_key="test-key")
    assert settings.log_level == "INFO"
    assert settings.api_prefix == "/api/v1"


def test_overrides_from_env(monkeypatch):
    """Environment variables override defaults."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("API_PREFIX", "/api/v2")

    settings = Settings()

    assert settings.api_prefix == "/api/v2"
