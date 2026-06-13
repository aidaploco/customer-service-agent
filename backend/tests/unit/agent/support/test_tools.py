from unittest.mock import MagicMock, patch

from agent.support.tools import (
    _create_ticket,
    _get_system_status,
    _get_ticket_status,
    _search_knowledge_base,
)


# _get_system_status


def test_get_system_status_operational():
    data = {
        "overall": "operational",
        "components": {"API": "operational", "Dashboard": "operational"},
        "active_incidents": [],
    }
    svc = MagicMock(get_system_status=MagicMock(return_value=data))
    with patch("agent.support.tools.get_support_service", return_value=svc):
        result = _get_system_status()
    assert "Operational" in result
    assert "No active incidents" in result
    assert "API" in result


def test_get_system_status_with_incidents():
    data = {
        "overall": "degraded_performance",
        "components": {"Webhooks": "degraded_performance"},
        "active_incidents": [
            {
                "severity": "minor",
                "title": "Webhook delays",
                "update": "Under investigation.",
            }
        ],
    }
    svc = MagicMock(get_system_status=MagicMock(return_value=data))
    with patch("agent.support.tools.get_support_service", return_value=svc):
        result = _get_system_status()
    assert "Webhook delays" in result
    assert "Minor" in result
    assert "Under investigation" in result


def test_get_system_status_formats_overall():
    data = {"overall": "partial_outage", "components": {}, "active_incidents": []}
    svc = MagicMock(get_system_status=MagicMock(return_value=data))
    with patch("agent.support.tools.get_support_service", return_value=svc):
        result = _get_system_status()
    assert "Partial outage" in result


# _search_knowledge_base


def test_search_knowledge_base_found():
    articles = [
        {"title": "Getting started", "summary": "How to authenticate."},
        {"title": "Webhooks guide", "summary": "Configure webhooks."},
    ]
    svc = MagicMock(search_knowledge_base=MagicMock(return_value=articles))
    with patch("agent.support.tools.get_support_service", return_value=svc):
        result = _search_knowledge_base("webhooks")
    assert "Getting started" in result
    assert "Webhooks guide" in result
    assert "How to authenticate" in result


def test_search_knowledge_base_no_results():
    svc = MagicMock(search_knowledge_base=MagicMock(return_value=[]))
    with patch("agent.support.tools.get_support_service", return_value=svc):
        result = _search_knowledge_base("something obscure")
    assert "No knowledge base articles found" in result


# _create_ticket


def test_create_ticket_returns_formatted_response():
    data = {
        "ticket_id": "BL-12345",
        "subject": "Login issue",
        "status": "open",
        "email": "user@example.com",
    }
    svc = MagicMock(create_ticket=MagicMock(return_value=data))
    with patch("agent.support.tools.get_support_service", return_value=svc):
        result = _create_ticket("user@example.com", "Login issue", "Can't log in")
    assert "BL-12345" in result
    assert "Login issue" in result
    assert "Open" in result
    assert "user@example.com" in result


# _get_ticket_status


def test_get_ticket_status_found():
    data = {
        "subject": "API rate limiting issue",
        "status": "in_progress",
        "created": "2026-04-28",
        "assigned_to": "Tier 2 Support",
    }
    svc = MagicMock(get_ticket=MagicMock(return_value=data))
    with patch("agent.support.tools.get_support_service", return_value=svc):
        result = _get_ticket_status("BL-10001")
    assert "BL-10001" in result
    assert "API rate limiting issue" in result
    assert "In progress" in result
    assert "Tier 2 Support" in result


def test_get_ticket_status_with_resolution():
    data = {
        "subject": "Webhook config",
        "status": "resolved",
        "created": "2026-04-25",
        "resolution": "Updated endpoint URL.",
    }
    svc = MagicMock(get_ticket=MagicMock(return_value=data))
    with patch("agent.support.tools.get_support_service", return_value=svc):
        result = _get_ticket_status("bl-10002")
    assert "BL-10002" in result
    assert "Updated endpoint URL" in result


def test_get_ticket_status_not_found():
    svc = MagicMock(get_ticket=MagicMock(return_value=None))
    with patch("agent.support.tools.get_support_service", return_value=svc):
        result = _get_ticket_status("BL-99999")
    assert "No ticket found" in result
    assert "BL-99999" in result


def test_get_ticket_status_no_assigned_to():
    data = {
        "subject": "Export question",
        "status": "open",
        "created": "2026-05-01",
    }
    svc = MagicMock(get_ticket=MagicMock(return_value=data))
    with patch("agent.support.tools.get_support_service", return_value=svc):
        result = _get_ticket_status("BL-10003")
    assert "assigned_to" not in result
    assert "Export question" in result
