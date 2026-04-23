from functools import lru_cache

from fastapi import APIRouter, Depends

from api.schemas.chat import ChatRequest, ChatResponse
from api.services.chat import ChatService

router = APIRouter()


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    return ChatService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    return await service.process_message(
        session_id=request.session_id,
        message=request.message,
    )
