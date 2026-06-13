from unittest.mock import MagicMock, patch

import pytest

from observability import setup_tracing


@pytest.fixture(autouse=True)
def clear_tracing_cache():
    setup_tracing.cache_clear()
    yield
    setup_tracing.cache_clear()


def test_setup_tracing_disabled_when_no_endpoint(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    mock_settings = MagicMock()
    mock_settings.phoenix_collector_endpoint = None
    with patch("observability.get_settings", return_value=mock_settings):
        with patch("observability.register") as mock_register:
            setup_tracing()
            mock_register.assert_not_called()


def test_setup_tracing_calls_register_when_endpoint_set(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    mock_settings = MagicMock()
    mock_settings.phoenix_collector_endpoint = "http://localhost:6006/v1/traces"
    with patch("observability.get_settings", return_value=mock_settings):
        with patch("observability.register") as mock_register:
            setup_tracing()
            mock_register.assert_called_once_with(
                endpoint="http://localhost:6006/v1/traces",
                project_name="customer-service-agent",
                auto_instrument=True,
            )


def test_setup_tracing_cached_second_call_is_noop(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    mock_settings = MagicMock()
    mock_settings.phoenix_collector_endpoint = "http://localhost:6006/v1/traces"
    with patch("observability.get_settings", return_value=mock_settings):
        with patch("observability.register") as mock_register:
            setup_tracing()
            setup_tracing()
            assert mock_register.call_count == 1
