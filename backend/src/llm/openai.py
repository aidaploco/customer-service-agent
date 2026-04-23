from __future__ import annotations

import functools

from agents.models.openai_responses import OpenAIResponsesModel
from openai import AsyncOpenAI

from config import get_settings


@functools.lru_cache(maxsize=1)
def _get_async_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=get_settings().openai_api_key)


def get_openai_model() -> OpenAIResponsesModel:
    return OpenAIResponsesModel(model=get_settings().openai_model, openai_client=_get_async_client())
