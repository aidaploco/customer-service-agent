import pytest
from pydantic import ValidationError

from config import Settings, get_settings


def test_missing_api_key_raises():
    """Settings must fail fast when OPENAI_API_KEY is absent."""
    with pytest.raises(ValidationError):
        Settings(openai_api_key=None)


def test_default_values(openai_env):
    """Confirm defaults match expected values."""
    settings = get_settings()
    assert settings.openai_model == "gpt-4o"
    assert settings.log_level == "DEBUG"
    assert settings.api_prefix == "/api/v1"


def test_overrides_from_env(monkeypatch):
    """Environment variables override defaults."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("API_PREFIX", "/api/v2")

    settings = Settings()

    assert settings.openai_model == "gpt-4o-mini"
    assert settings.api_prefix == "/api/v2"
