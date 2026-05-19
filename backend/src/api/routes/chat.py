from functools import lru_cache

from fastapi import APIRouter, Depends

from api.schemas.chat import AgentInfo, ChatRequest, ChatResponse
from api.services.chat import ChatService
from store.redis_store import get_redis_store

router = APIRouter()


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    """Return the ChatService singleton."""
    return ChatService(store=get_redis_store())


@router.get("/agents", response_model=list[AgentInfo])
async def get_agents(
    service: ChatService = Depends(get_chat_service),
) -> list[AgentInfo]:
    """Return the static agent registry — call once on frontend mount."""
    return service.agents


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Accept a user message and return the agent's response."""
    return await service.process_message(
        session_id=request.session_id,
        message=request.message,
    )
