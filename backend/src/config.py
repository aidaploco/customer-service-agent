from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    openai_api_key: str
    supervisor_model: str = "gpt-4o-mini"
    eval_judge_model: str = "gpt-5.4-mini-2026-03-17"
    billing_model: str = "gpt-4o"
    support_model: str = "gpt-4o"
    guardrail_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    max_message_length: int = 1000
    rag_top_k: int = 2
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    redis_url: str = "redis://localhost:6379"
    session_ttl_seconds: int = 3600
    postgres_url: str = "postgresql://brightloop:brightloop@localhost:5432/brightloop"
    postgres_pool_size: int = 10
    phoenix_collector_endpoint: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
