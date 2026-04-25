from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Incoming chat message from the client."""

    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Agent response returned to the client."""

    session_id: str
    message: str
    agent: str
