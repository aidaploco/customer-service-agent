from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    openai_api_key: str
    openai_model: str = "gpt-4o"
    guardrail_model: str = "gpt-4o-mini"
    log_level: str = "DEBUG"
    api_prefix: str = "/api/v1"
    redis_url: str = "redis://localhost:6379"
    session_ttl_seconds: int = 3600


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
