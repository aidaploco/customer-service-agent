import time
from datetime import datetime, timezone

from agents import Runner

from agent.supervisor import create_supervisor_agent
from api.schemas.chat import ChatResponse
from store.base import BaseConversationStore
from utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """Orchestrates agent execution for a single chat turn."""

    def __init__(self, store: BaseConversationStore) -> None:
        self._agent = create_supervisor_agent()
        self._store = store

    async def process_message(self, session_id: str, message: str) -> ChatResponse:
        """Run the agent on the given message and return the response."""
        state = await self._store.get_or_create(session_id)

        if state.messages:
            input_ = state.messages + [{"role": "user", "content": message}]
        else:
            input_ = message

        start = time.perf_counter()
        result = await Runner.run(starting_agent=self._agent, input=input_)
        duration_ms = (time.perf_counter() - start) * 1000

        state.messages = result.to_input_list()
        state.last_activity = datetime.now(timezone.utc)
        await self._store.save(state)

        logger.info(
            "session=%s agent=%s duration=%.1fms",
            session_id,
            result.last_agent.name,
            duration_ms,
        )
        return ChatResponse(
            session_id=session_id,
            message=result.final_output,
            agent=result.last_agent.name,
        )
