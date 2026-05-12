from __future__ import annotations

import functools

from agents.models.openai_responses import OpenAIResponsesModel
from openai import AsyncOpenAI

from config import get_settings


@functools.lru_cache(maxsize=1)
def _get_async_client() -> AsyncOpenAI:
    """Return a cached AsyncOpenAI client authenticated via settings."""
    return AsyncOpenAI(api_key=get_settings().openai_api_key)


def get_openai_model() -> OpenAIResponsesModel:
    """Return an OpenAIResponsesModel ready to pass to an Agent."""
    return OpenAIResponsesModel(
        model=get_settings().openai_model, openai_client=_get_async_client()
    )


def get_guardrail_model() -> OpenAIResponsesModel:
    """Return a model instance for guardrail classifier agents (uses the cheaper guardrail_model)."""
    return OpenAIResponsesModel(
        model=get_settings().guardrail_model, openai_client=_get_async_client()
    )
