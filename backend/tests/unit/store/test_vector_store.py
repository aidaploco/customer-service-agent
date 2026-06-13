from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import store.vector_store as vs


@pytest.fixture(autouse=True)
def reset_pool():
    original = vs._pool
    vs._pool = None
    yield
    vs._pool = original


def _async_cm(return_value):
    """Return an async context manager mock that yields return_value."""
    cm = AsyncMock()
    cm.__aenter__.return_value = return_value
    cm.__aexit__.return_value = AsyncMock(return_value=None)
    return cm


# close_pg_pool


async def test_close_pg_pool_when_none_is_noop():
    vs._pool = None
    await vs.close_pg_pool()  # should not raise


async def test_close_pg_pool_calls_close_on_pool():
    mock_pool = AsyncMock()
    vs._pool = mock_pool
    await vs.close_pg_pool()
    mock_pool.close.assert_called_once()
    assert vs._pool is None


# _get_pool


def test_get_pool_raises_when_not_initialized():
    vs._pool = None
    with pytest.raises(RuntimeError, match="not initialized"):
        vs._get_pool()


def test_get_pool_returns_pool_when_set():
    mock_pool = MagicMock()
    vs._pool = mock_pool
    assert vs._get_pool() is mock_pool


# init_db


async def test_init_db_creates_extension_and_table():
    mock_conn = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "store.vector_store.psycopg.AsyncConnection.connect", return_value=mock_conn
    ):
        with patch("store.vector_store.register_vector_async", new_callable=AsyncMock):
            with patch("store.vector_store.get_settings") as mock_settings:
                mock_settings.return_value.postgres_url = "postgresql://test"
                mock_settings.return_value.embedding_dim = 1536
                await vs.init_db()

    calls = [str(c) for c in mock_conn.execute.call_args_list]
    assert any("vector" in c for c in calls)
    assert any("knowledge_chunks" in c for c in calls)


# hash_matches


def _make_cur(fetchone=None, fetchall=None) -> AsyncMock:
    """cursor() is a sync call returning an async context manager."""
    cur = AsyncMock()
    cur.fetchone.return_value = fetchone
    cur.fetchall.return_value = fetchall or []
    cur.__aenter__ = AsyncMock(return_value=cur)
    cur.__aexit__ = AsyncMock(return_value=None)
    return cur


def _make_conn(cur: AsyncMock) -> AsyncMock:
    conn = AsyncMock()
    # cursor() is sync (returns an async cm, not a coroutine)
    conn.cursor = MagicMock(return_value=cur)
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=None)
    return conn


async def test_hash_matches_returns_true_when_found():
    cur = _make_cur(fetchone=(1,))
    conn = _make_conn(cur)

    with patch("store.vector_store.psycopg.AsyncConnection.connect", return_value=conn):
        with patch("store.vector_store.get_settings") as mock_settings:
            mock_settings.return_value.postgres_url = "postgresql://test"
            result = await vs.hash_matches("company.md", "abc123")

    assert result is True


async def test_hash_matches_returns_false_when_not_found():
    cur = _make_cur(fetchone=None)
    conn = _make_conn(cur)

    with patch("store.vector_store.psycopg.AsyncConnection.connect", return_value=conn):
        with patch("store.vector_store.get_settings") as mock_settings:
            mock_settings.return_value.postgres_url = "postgresql://test"
            result = await vs.hash_matches("company.md", "notfound")

    assert result is False


# replace_source_chunks


async def test_replace_source_chunks_deletes_then_inserts():
    cur = _make_cur()
    conn = _make_conn(cur)

    records = [
        {
            "source": "company.md",
            "chunk_index": 0,
            "content": "chunk0",
            "source_hash": "h1",
            "embedding": [0.1],
        },
    ]

    with patch("store.vector_store.psycopg.AsyncConnection.connect", return_value=conn):
        with patch("store.vector_store.register_vector_async", new_callable=AsyncMock):
            with patch("store.vector_store.get_settings") as mock_settings:
                mock_settings.return_value.postgres_url = "postgresql://test"
                await vs.replace_source_chunks("company.md", records)

    execute_calls = [str(c) for c in conn.execute.call_args_list]
    assert any("DELETE" in c for c in execute_calls)
    cur.executemany.assert_called_once()


# search_chunks


async def test_search_chunks_returns_content_list():
    cur = _make_cur(fetchall=[("chunk A",), ("chunk B",)])
    conn = _make_conn(cur)

    mock_pool = MagicMock()
    mock_pool.connection.return_value = conn
    vs._pool = mock_pool

    result = await vs.search_chunks([0.1, 0.2, 0.3], top_k=2)

    assert result == ["chunk A", "chunk B"]
    cur.execute.assert_called_once()
