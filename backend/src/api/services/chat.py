import time

from agents import Runner

from agent.supervisor import create_supervisor_agent
from api.schemas.chat import ChatResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    def __init__(self) -> None:
        self._agent = create_supervisor_agent()

    async def process_message(self, session_id: str, message: str) -> ChatResponse:
        start = time.perf_counter()
        result = await Runner.run(starting_agent=self._agent, input=message)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "session=%s agent=%s duration=%.1fms",
            session_id,
            result.last_agent.name,
            duration_ms,
        )
        return ChatResponse(
            message=result.final_output,
            agent=result.last_agent.name,
        )
