from functools import lru_cache

import redis.asyncio as aioredis

from api.schemas.conversation import ConversationState
from config import get_settings
from store.base import BaseConversationStore


class RedisConversationStore(BaseConversationStore):
    """Conversation state store backed by Redis."""

    def __init__(
        self,
        client: aioredis.Redis,
        ttl: int,
        key_prefix: str = "session:",
    ) -> None:
        self._client = client
        self._ttl = ttl
        self._key_prefix = key_prefix

    def _key(self, session_id: str) -> str:
        """Return the namespaced Redis key for a session."""
        return f"{self._key_prefix}{session_id}"

    async def get_or_create(self, session_id: str) -> ConversationState:
        """Return existing state or a fresh ConversationState if not found."""
        data = await self._client.get(self._key(session_id))
        if data is None:
            return ConversationState(session_id=session_id)
        return ConversationState.model_validate_json(data)

    async def save(self, state: ConversationState) -> None:
        """Serialise and persist state, resetting the TTL."""
        await self._client.setex(
            self._key(state.session_id),
            self._ttl,
            state.model_dump_json(),
        )

    async def delete(self, session_id: str) -> None:
        """Delete the state for session_id."""
        await self._client.delete(self._key(session_id))

    async def exists(self, session_id: str) -> bool:
        """Return True if a state exists for session_id."""
        return bool(await self._client.exists(self._key(session_id)))

    async def ping(self) -> bool:
        """Return True if Redis is reachable."""
        try:
            return bool(await self._client.ping())
        except Exception:
            return False

    async def clear_all(self) -> int:
        """Delete all sessions via SCAN. Returns count of deleted keys."""
        deleted = 0
        cursor = 0
        while True:
            cursor, keys = await self._client.scan(
                cursor, match=f"{self._key_prefix}*", count=100
            )
            if keys:
                deleted += await self._client.delete(*keys)
            if cursor == 0:
                break
        return deleted


@lru_cache(maxsize=1)
def get_redis_store() -> RedisConversationStore:
    """Return the cached RedisConversationStore singleton."""
    settings = get_settings()
    pool = aioredis.ConnectionPool.from_url(
        settings.redis_url,
        max_connections=10,
    )
    client = aioredis.Redis(connection_pool=pool)
    return RedisConversationStore(client=client, ttl=settings.session_ttl_seconds)
