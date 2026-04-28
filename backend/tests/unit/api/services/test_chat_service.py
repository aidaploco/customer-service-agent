from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.schemas.chat import ChatResponse
from api.schemas.conversation import ConversationState
from api.services.chat import ChatService


@pytest.fixture
def mock_store() -> AsyncMock:
    store = AsyncMock()
    store.get_or_create.return_value = ConversationState(session_id="session-1")
    return store


@pytest.fixture
def mock_registry() -> dict:
    supervisor = MagicMock()
    supervisor.name = "Supervisor"
    return {"Supervisor": supervisor}


@pytest.fixture
def service(openai_env, mock_store, mock_registry):
    """ChatService with registry and store mocked out."""
    with patch("api.services.chat.build_agent_registry", return_value=mock_registry):
        yield ChatService(store=mock_store)


@pytest.fixture
def mock_run_result():
    result = MagicMock()
    result.final_output = "Hello! I'm Zara, how can I help?"
    result.last_agent.name = "Supervisor"
    result.to_input_list.return_value = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello! I'm Zara, how can I help?"},
    ]
    return result


async def test_process_message_returns_chat_response(
    service, mock_store, mock_run_result
):
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_run_result,
    ):
        response = await service.process_message("session-1", "Hi")
    assert isinstance(response, ChatResponse)


async def test_process_message_content(service, mock_store, mock_run_result):
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_run_result,
    ):
        response = await service.process_message("session-1", "Hi")
    assert response.session_id == "session-1"
    assert response.message == "Hello! I'm Zara, how can I help?"
    assert response.agent == "Supervisor"


async def test_process_message_first_turn_passes_string_input(
    service, mock_store, mock_run_result
):
    """On the first turn (empty history) the raw message string is passed directly."""
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_run_result,
    ) as mock_run:
        await service.process_message("session-1", "What is my billing cycle?")
    _, kwargs = mock_run.call_args
    assert kwargs["input"] == "What is my billing cycle?"


async def test_process_message_subsequent_turn_prepends_history(
    service, mock_store, mock_run_result
):
    """On subsequent turns, stored history is prepended to the new user message."""
    existing_history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello! I'm Zara, how can I help?"},
    ]
    mock_store.get_or_create.return_value = ConversationState(
        session_id="session-1", messages=existing_history
    )
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_run_result,
    ) as mock_run:
        await service.process_message("session-1", "What is my billing?")
    _, kwargs = mock_run.call_args
    assert kwargs["input"] == existing_history + [
        {"role": "user", "content": "What is my billing?"}
    ]


async def test_process_message_saves_updated_history(
    service, mock_store, mock_run_result
):
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_run_result,
    ):
        await service.process_message("session-1", "Hi")
    mock_store.save.assert_called_once()
    saved_state = mock_store.save.call_args[0][0]
    assert saved_state.messages == mock_run_result.to_input_list.return_value


async def test_process_message_persists_current_agent_name(
    service, mock_store, mock_run_result
):
    """current_agent_name in state is updated to the last agent after each turn."""
    mock_run_result.last_agent.name = "Billing"
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_run_result,
    ):
        await service.process_message("session-1", "I have a billing question")
    saved_state = mock_store.save.call_args[0][0]
    assert saved_state.current_agent_name == "Billing"


async def test_process_message_uses_current_agent_from_state(
    service, mock_store, mock_registry, mock_run_result
):
    """Subsequent turns start from the agent stored in state, not always Supervisor."""
    billing_agent = MagicMock()
    billing_agent.name = "Billing"
    mock_registry["Billing"] = billing_agent
    mock_store.get_or_create.return_value = ConversationState(
        session_id="session-1",
        current_agent_name="Billing",
        messages=[{"role": "user", "content": "Hi"}],
    )
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_run_result,
    ) as mock_run:
        await service.process_message("session-1", "What is my invoice?")
    _, kwargs = mock_run.call_args
    assert kwargs["starting_agent"] is billing_agent


async def test_process_message_falls_back_to_supervisor_for_unknown_agent(
    service, mock_store, mock_registry, mock_run_result
):
    """Falls back to Supervisor if state holds an unrecognised agent name."""
    mock_store.get_or_create.return_value = ConversationState(
        session_id="session-1", current_agent_name="UnknownAgent"
    )
    with patch(
        "api.services.chat.Runner.run",
        new_callable=AsyncMock,
        return_value=mock_run_result,
    ) as mock_run:
        await service.process_message("session-1", "Hi")
    _, kwargs = mock_run.call_args
    assert kwargs["starting_agent"] is mock_registry["Supervisor"]
