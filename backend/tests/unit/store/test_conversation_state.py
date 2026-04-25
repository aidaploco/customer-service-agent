from api.schemas.conversation import ConversationState


def test_default_agent_name():
    state = ConversationState(session_id="abc")
    assert state.current_agent_name == "Supervisor"


def test_default_messages_empty():
    state = ConversationState(session_id="abc")
    assert state.messages == []


def test_timestamps_set_on_creation():
    state = ConversationState(session_id="abc")
    assert state.created_at is not None
    assert state.last_activity is not None


def test_serialisation_roundtrip():
    state = ConversationState(
        session_id="abc",
        current_agent_name="Billing",
        messages=[{"role": "user", "content": "Hi"}],
    )
    restored = ConversationState.model_validate_json(state.model_dump_json())
    assert restored.session_id == state.session_id
    assert restored.current_agent_name == state.current_agent_name
    assert restored.messages == state.messages
    assert restored.created_at == state.created_at
