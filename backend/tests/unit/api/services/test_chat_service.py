from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.schemas.chat import ChatResponse
from api.services.chat import ChatService


@pytest.fixture
def service(openai_env):
    """ChatService with supervisor agent creation mocked out."""
    with patch("api.services.chat.create_supervisor_agent", return_value=MagicMock()):
        yield ChatService()


@pytest.fixture
def mock_run_result():
    result = MagicMock()
    result.final_output = "Hello! I'm Zara, how can I help?"
    result.last_agent.name = "Supervisor"
    return result


async def test_process_message_returns_chat_response(service, mock_run_result):
    with patch("api.services.chat.Runner.run", new_callable=AsyncMock, return_value=mock_run_result):
        response = await service.process_message("session-1", "Hi")
    assert isinstance(response, ChatResponse)


async def test_process_message_content(service, mock_run_result):
    with patch("api.services.chat.Runner.run", new_callable=AsyncMock, return_value=mock_run_result):
        response = await service.process_message("session-1", "Hi")
    assert response.message == "Hello! I'm Zara, how can I help?"
    assert response.agent == "Supervisor"


async def test_process_message_passes_input_to_runner(service, mock_run_result):
    with patch("api.services.chat.Runner.run", new_callable=AsyncMock, return_value=mock_run_result) as mock_run:
        await service.process_message("session-1", "What is my billing cycle?")
    mock_run.assert_called_once()
    _, kwargs = mock_run.call_args
    assert kwargs["input"] == "What is my billing cycle?"
