from unittest.mock import AsyncMock

import pytest
import redis.asyncio as aioredis

from api.schemas.conversation import ConversationState
from store.redis_store import RedisConversationStore


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Async mock of the Redis client."""
    return AsyncMock()


@pytest.fixture
def store(mock_redis: AsyncMock) -> RedisConversationStore:
    """Store instance with a test-scoped key prefix to isolate from real data."""
    return RedisConversationStore(client=mock_redis, ttl=3600, key_prefix="test:")


async def test_get_or_create_returns_fresh_state_when_missing(
    store: RedisConversationStore, mock_redis: AsyncMock
) -> None:
    mock_redis.get.return_value = None
    state = await store.get_or_create("session-1")
    assert state.session_id == "session-1"
    assert state.messages == []
    assert state.current_agent_name == "Supervisor"


async def test_get_or_create_returns_existing_state(
    store: RedisConversationStore, mock_redis: AsyncMock
) -> None:
    existing = ConversationState(session_id="session-1", current_agent_name="Billing")
    mock_redis.get.return_value = existing.model_dump_json().encode()
    state = await store.get_or_create("session-1")
    assert state.session_id == "session-1"
    assert state.current_agent_name == "Billing"


async def test_save_calls_setex_with_correct_args(
    store: RedisConversationStore, mock_redis: AsyncMock
) -> None:
    state = ConversationState(session_id="session-1")
    await store.save(state)
    mock_redis.setex.assert_called_once_with(
        "test:session-1", 3600, state.model_dump_json()
    )


async def test_delete_calls_delete_with_correct_key(
    store: RedisConversationStore, mock_redis: AsyncMock
) -> None:
    await store.delete("session-1")
    mock_redis.delete.assert_called_once_with("test:session-1")


async def test_exists_returns_true_when_key_present(
    store: RedisConversationStore, mock_redis: AsyncMock
) -> None:
    mock_redis.exists.return_value = 1
    assert await store.exists("session-1") is True


async def test_exists_returns_false_when_key_absent(
    store: RedisConversationStore, mock_redis: AsyncMock
) -> None:
    mock_redis.exists.return_value = 0
    assert await store.exists("session-1") is False


async def test_ping_returns_true_when_reachable(
    store: RedisConversationStore, mock_redis: AsyncMock
) -> None:
    mock_redis.ping.return_value = True
    assert await store.ping() is True


async def test_ping_returns_false_on_connection_error(
    store: RedisConversationStore, mock_redis: AsyncMock
) -> None:
    mock_redis.ping.side_effect = ConnectionError("Redis unreachable")
    assert await store.ping() is False


async def test_clear_all_returns_zero_when_no_sessions(
    store: RedisConversationStore, mock_redis: AsyncMock
) -> None:
    mock_redis.scan.return_value = (0, [])
    result = await store.clear_all()
    assert result == 0
    mock_redis.delete.assert_not_called()


async def test_clear_all_deletes_across_multiple_scan_pages(
    store: RedisConversationStore, mock_redis: AsyncMock
) -> None:
    mock_redis.scan.side_effect = [
        (10, [b"test:session-1", b"test:session-2"]),
        (0, [b"test:session-3"]),
    ]
    mock_redis.delete.side_effect = [2, 1]
    result = await store.clear_all()
    assert result == 3
    assert mock_redis.delete.call_count == 2


async def test_key_prefix_applied_to_all_operations(
    mock_redis: AsyncMock,
) -> None:
    store = RedisConversationStore(client=mock_redis, ttl=60, key_prefix="custom:")
    mock_redis.get.return_value = None
    await store.get_or_create("abc")
    mock_redis.get.assert_called_once_with("custom:abc")


class TestRetry:
    async def test_get_or_create_retries_on_redis_error(
        self, store: RedisConversationStore, mock_redis: AsyncMock
    ) -> None:
        mock_redis.get.side_effect = [
            aioredis.RedisError("transient"),
            None,
        ]
        state = await store.get_or_create("session-1")
        assert state.session_id == "session-1"
        assert mock_redis.get.call_count == 2

    async def test_save_retries_on_redis_error(
        self, store: RedisConversationStore, mock_redis: AsyncMock
    ) -> None:
        mock_redis.setex.side_effect = [
            aioredis.RedisError("transient"),
            None,
        ]
        state = ConversationState(session_id="session-1")
        await store.save(state)
        assert mock_redis.setex.call_count == 2

    async def test_raises_after_max_attempts(
        self, store: RedisConversationStore, mock_redis: AsyncMock
    ) -> None:
        mock_redis.get.side_effect = aioredis.RedisError("persistent")
        with pytest.raises(aioredis.RedisError):
            await store.get_or_create("session-1")
        assert mock_redis.get.call_count == 3
