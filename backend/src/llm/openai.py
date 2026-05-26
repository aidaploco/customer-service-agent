from __future__ import annotations

import functools
import time

from agents.models.openai_responses import OpenAIResponsesModel
from openai import AsyncOpenAI

from config import get_settings

_embed_cache: dict[str, tuple[list[float], float]] = {}
_EMBED_CACHE_TTL = 60.0


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


async def get_embedding(text: str) -> list[float]:
    """Return the embedding for text, served from a 60-second in-process cache.

    Both the intent classifier and the RAG tool call this, so a repeated query
    (e.g. the user's message passed verbatim to search_company_info) costs 0ms
    on the second call within the TTL window.
    """
    cached = _embed_cache.get(text)
    if cached is not None:
        embedding, ts = cached
        if time.time() - ts < _EMBED_CACHE_TTL:
            return embedding
        del _embed_cache[text]

    response = await get_async_client().embeddings.create(
        model=get_settings().embedding_model, input=text
    )
    embedding = response.data[0].embedding
    _embed_cache[text] = (embedding, time.time())
    return embedding
