from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.app import app
from api.middleware.request_id import REQUEST_ID_HEADER
from api.routes.chat import get_chat_service
from api.schemas.conversation import ConversationState
from api.services.chat import ChatService


@pytest.fixture
def mock_store() -> AsyncMock:
    store = AsyncMock()
    store.get_or_create.return_value = ConversationState(
        session_id="00000000-0000-4000-8000-000000000001"
    )
    return store


@pytest.fixture
def mock_registry() -> dict:
    supervisor = MagicMock()
    supervisor.name = "Supervisor"
    supervisor.handoff_description = "Routes to the right agent."
    supervisor.tools = []
    supervisor.handoffs = []
    return {"Supervisor": supervisor}


@pytest.fixture
def mock_service(openai_env, mock_store, mock_registry):
    """ChatService with all external deps mocked."""
    with patch("api.services.chat.build_agent_registry", return_value=mock_registry):
        service = ChatService(store=mock_store)
    return service


@pytest.fixture
def client(mock_service):
    """Full app with the real middleware stack but a mocked ChatService."""
    app.dependency_overrides[get_chat_service] = lambda: mock_service
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def mock_runner_result():
    result = MagicMock()
    result.final_output = "Hello! I'm Zara, how can I help?"
    result.last_agent.name = "Supervisor"
    result.to_input_list.return_value = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello! I'm Zara, how can I help?"},
    ]
    result.input_guardrail_results = []
    result.new_items = []
    return result


def test_chat_returns_200(client, mock_runner_result):
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_runner_result,
    ):
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "00000000-0000-4000-8000-000000000001",
                "message": "Hi",
            },
        )
    assert response.status_code == 200


def test_chat_response_shape(client, mock_runner_result):
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_runner_result,
    ):
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "00000000-0000-4000-8000-000000000001",
                "message": "Hi",
            },
        )
    body = response.json()
    assert body["session_id"] == "00000000-0000-4000-8000-000000000001"
    assert body["message"] == "Hello! I'm Zara, how can I help?"
    assert body["agent"]["name"] == "Supervisor"


def test_chat_missing_message_returns_422(client):
    response = client.post(
        "/api/v1/chat", json={"session_id": "00000000-0000-4000-8000-000000000001"}
    )
    assert response.status_code == 422
    body = response.json()
    assert "error" in body
    assert "message" in body["error"].lower()


def test_chat_missing_session_id_returns_422(client):
    response = client.post("/api/v1/chat", json={"message": "Hi"})
    assert response.status_code == 422
    body = response.json()
    assert "error" in body
    assert "session_id" in body["error"].lower()


def test_malformed_json_returns_422_with_friendly_error(client):
    response = client.post(
        "/api/v1/chat",
        content=b'{"session_id": "00000000-0000-4000-8000-000000000001", "message": "say "hello""}',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    body = response.json()
    assert "error" in body
    assert "json" in body["error"].lower()


def test_request_id_present_in_response(client, mock_runner_result):
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_runner_result,
    ):
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "00000000-0000-4000-8000-000000000001",
                "message": "Hi",
            },
        )
    assert REQUEST_ID_HEADER in response.headers


def test_client_request_id_is_preserved(client, mock_runner_result):
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_runner_result,
    ):
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "00000000-0000-4000-8000-000000000001",
                "message": "Hi",
            },
            headers={REQUEST_ID_HEADER: "my-trace-id"},
        )
    assert response.headers[REQUEST_ID_HEADER] == "my-trace-id"
