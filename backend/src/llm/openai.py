from __future__ import annotations

import functools

from agents.models.openai_responses import OpenAIResponsesModel
from openai import AsyncOpenAI

from config import get_settings


@functools.lru_cache(maxsize=1)
def get_async_client() -> AsyncOpenAI:
    """Return the cached AsyncOpenAI client."""
    return AsyncOpenAI(api_key=get_settings().openai_api_key)


def get_billing_model() -> OpenAIResponsesModel:
    """Return a model instance for the billing agent."""
    return OpenAIResponsesModel(
        model=get_settings().billing_model, openai_client=get_async_client()
    )


def get_support_model() -> OpenAIResponsesModel:
    """Return a model instance for the support agent."""
    return OpenAIResponsesModel(
        model=get_settings().support_model, openai_client=get_async_client()
    )


def get_supervisor_model() -> OpenAIResponsesModel:
    """Return a model instance for the supervisor agent (uses the cheaper supervisor_model)."""
    return OpenAIResponsesModel(
        model=get_settings().supervisor_model, openai_client=get_async_client()
    )


def get_guardrail_model() -> OpenAIResponsesModel:
    """Return a model instance for guardrail classifier agents (uses the cheaper guardrail_model)."""
    return OpenAIResponsesModel(
        model=get_settings().guardrail_model, openai_client=get_async_client()
    )
