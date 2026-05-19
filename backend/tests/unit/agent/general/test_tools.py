from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agent.general.tools import _search_company_info


def _make_embedding_response(n: int = 1) -> MagicMock:
    embedding = [0.1] * 1536
    response = MagicMock()
    response.data = [MagicMock(embedding=embedding) for _ in range(n)]
    return response


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.embeddings.create = AsyncMock(return_value=_make_embedding_response())
    return client


async def test_returns_joined_chunks(openai_env, mock_client):
    chunks = ["Brightloop was founded in 2021.", "Headquartered in San Francisco."]
    with patch("agent.general.tools.get_async_client", return_value=mock_client), \
         patch("agent.general.tools.search_chunks", new_callable=AsyncMock, return_value=chunks):
        result = await _search_company_info("when was brightloop founded")
    assert "Brightloop was founded in 2021." in result
    assert "Headquartered in San Francisco." in result


async def test_no_results_returns_fallback(openai_env, mock_client):
    with patch("agent.general.tools.get_async_client", return_value=mock_client), \
         patch("agent.general.tools.search_chunks", new_callable=AsyncMock, return_value=[]):
        result = await _search_company_info("something obscure")
    assert "No information found" in result


async def test_passes_query_embedding_to_search(openai_env, mock_client):
    with patch("agent.general.tools.get_async_client", return_value=mock_client), \
         patch("agent.general.tools.search_chunks", new_callable=AsyncMock, return_value=["chunk"]) as mock_search:
        await _search_company_info("security certifications")
    embedding_used = mock_search.call_args[0][0]
    assert len(embedding_used) == 1536
