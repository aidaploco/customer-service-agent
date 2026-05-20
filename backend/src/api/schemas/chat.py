import uuid

from pydantic import BaseModel, field_validator


class AgentInfo(BaseModel):
    name: str
    description: str
    tools: list[str]
    handoffs: list[str]


class GuardrailResult(BaseModel):
    name: str
    passed: bool
    reasoning: str | None = None


class AgentEvent(BaseModel):
    type: str  # "handoff" | "tool_call" | "tool_output"
    agent: str
    content: str


class ChatRequest(BaseModel):
    """Incoming chat message from the client."""

    session_id: str
    message: str

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        try:
            uuid.UUID(v, version=4)
        except ValueError:
            raise ValueError("session_id must be a valid UUID v4")
        return v


class ChatResponse(BaseModel):
    """Agent response returned to the client."""

    session_id: str
    message: str
    agent: AgentInfo
    guardrails: list[GuardrailResult]
    events: list[AgentEvent]
