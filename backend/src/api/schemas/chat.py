from pydantic import BaseModel


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


class ChatResponse(BaseModel):
    """Agent response returned to the client."""

    session_id: str
    message: str
    agent: AgentInfo
    guardrails: list[GuardrailResult]
    events: list[AgentEvent]
