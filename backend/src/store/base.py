from typing import Protocol

from api.schemas.conversation import ConversationState


class BaseConversationStore(Protocol):
    """Interface for conversation state persistence."""

    async def get_or_create(self, session_id: str) -> ConversationState:
        """Return existing state for session_id, or a fresh one if none exists."""
        ...

    async def save(self, state: ConversationState) -> None:
        """Persist state, resetting the TTL."""
        ...

    async def delete(self, session_id: str) -> None:
        """Remove state for session_id."""
        ...

    async def exists(self, session_id: str) -> bool:
        """Return True if a state exists for session_id."""
        ...

    async def ping(self) -> bool:
        """Return True if the backing store is reachable."""
        ...

    async def clear_all(self) -> int:
        """Delete all sessions. Returns the number of deleted entries."""
        ...
