from unittest.mock import AsyncMock, patch

import pytest

from agent.general.tools import _search_company_info

_EMBEDDING = [0.1] * 1536


async def test_returns_joined_chunks(openai_env):
    chunks = ["Brightloop was founded in 2021.", "Headquartered in San Francisco."]
    with (
        patch(
            "agent.general.tools.get_embedding",
            new_callable=AsyncMock,
            return_value=_EMBEDDING,
        ),
        patch(
            "agent.general.tools.search_chunks",
            new_callable=AsyncMock,
            return_value=chunks,
        ),
    ):
        result = await _search_company_info("when was brightloop founded")
    assert "Brightloop was founded in 2021." in result
    assert "Headquartered in San Francisco." in result


async def test_no_results_returns_fallback(openai_env):
    with (
        patch(
            "agent.general.tools.get_embedding",
            new_callable=AsyncMock,
            return_value=_EMBEDDING,
        ),
        patch(
            "agent.general.tools.search_chunks", new_callable=AsyncMock, return_value=[]
        ),
    ):
        result = await _search_company_info("something obscure")
    assert "No information found" in result


async def test_passes_embedding_to_search(openai_env):
    with (
        patch(
            "agent.general.tools.get_embedding",
            new_callable=AsyncMock,
            return_value=_EMBEDDING,
        ),
        patch(
            "agent.general.tools.search_chunks",
            new_callable=AsyncMock,
            return_value=["chunk"],
        ) as mock_search,
    ):
        await _search_company_info("security certifications")
    embedding_used = mock_search.call_args[0][0]
    assert len(embedding_used) == 1536


async def test_search_exception_returns_fallback(openai_env):
    with (
        patch(
            "agent.general.tools.get_embedding",
            new_callable=AsyncMock,
            return_value=_EMBEDDING,
        ),
        patch(
            "agent.general.tools.search_chunks",
            new_callable=AsyncMock,
            side_effect=RuntimeError("pool not initialized"),
        ),
    ):
        result = await _search_company_info("what are your products")
    assert "unavailable" in result.lower()
    assert "brightloop.io" in result.lower()
