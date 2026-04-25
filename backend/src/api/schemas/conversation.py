from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ConversationState(BaseModel):
    """Persisted state for a single customer conversation."""

    session_id: str
    current_agent_name: str = "Supervisor"
    messages: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
