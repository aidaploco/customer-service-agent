from __future__ import annotations

import functools
import os

from agents.models.openai_responses import OpenAIResponsesModel
from openai import AsyncOpenAI


@functools.lru_cache(maxsize=1)
def _get_async_client() -> AsyncOpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY environment variable is not set."
        )
    return AsyncOpenAI(api_key=api_key)


def get_openai_model() -> OpenAIResponsesModel:
    """Return an OpenAIResponsesModel ready to pass to an Agent.

    Reads OPENAI_MODEL from the environment (defaults to gpt-4o).
    The underlying AsyncOpenAI client is constructed once and cached.
    """
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    return OpenAIResponsesModel(model=model, openai_client=_get_async_client())
