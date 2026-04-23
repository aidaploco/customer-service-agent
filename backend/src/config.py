from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    openai_api_key: str
    openai_model: str = "gpt-4o"
    log_level: str = "DEBUG"
    api_prefix: str = "/api/v1"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
