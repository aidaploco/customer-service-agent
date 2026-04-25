import pytest
import fakeredis.aioredis

from store.redis_store import RedisConversationStore


@pytest.fixture
async def store() -> RedisConversationStore:
    """Store backed by an in-memory fakeredis instance."""
    client = fakeredis.aioredis.FakeRedis()
    return RedisConversationStore(client=client, ttl=3600, key_prefix="test:")


async def test_save_and_retrieve_roundtrip(store: RedisConversationStore) -> None:
    state = await store.get_or_create("session-1")
    state.current_agent_name = "Billing"
    state.messages.append({"role": "user", "content": "Hello"})
    await store.save(state)

    retrieved = await store.get_or_create("session-1")
    assert retrieved.current_agent_name == "Billing"
    assert retrieved.messages == [{"role": "user", "content": "Hello"}]


async def test_get_or_create_returns_same_state_on_second_call(
    store: RedisConversationStore,
) -> None:
    first = await store.get_or_create("session-1")
    first.current_agent_name = "Billing"
    await store.save(first)

    second = await store.get_or_create("session-1")
    assert second.current_agent_name == "Billing"


async def test_exists_true_after_save(store: RedisConversationStore) -> None:
    state = await store.get_or_create("session-1")
    await store.save(state)
    assert await store.exists("session-1") is True


async def test_delete_removes_state(store: RedisConversationStore) -> None:
    state = await store.get_or_create("session-1")
    await store.save(state)
    await store.delete("session-1")
    assert await store.exists("session-1") is False


async def test_clear_all_removes_all_sessions(store: RedisConversationStore) -> None:
    for session_id in ("session-1", "session-2", "session-3"):
        await store.save(await store.get_or_create(session_id))

    deleted = await store.clear_all()

    assert deleted == 3
    for session_id in ("session-1", "session-2", "session-3"):
        assert await store.exists(session_id) is False


async def test_clear_all_only_removes_own_prefix(store: RedisConversationStore) -> None:
    """SCAN pattern matching must not touch keys from a different prefix."""
    other_store = RedisConversationStore(
        client=store._client, ttl=3600, key_prefix="other:"
    )
    await store.save(await store.get_or_create("session-1"))
    await other_store.save(await other_store.get_or_create("session-1"))

    await store.clear_all()

    assert await store.exists("session-1") is False
    assert await other_store.exists("session-1") is True
