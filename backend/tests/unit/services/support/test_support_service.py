import re

import pytest

from services.support.service import SupportService


@pytest.fixture
def service() -> SupportService:
    return SupportService()


class TestGetSystemStatus:
    def test_returns_overall_status(self, service):
        result = service.get_system_status()
        assert "overall" in result
        assert "components" in result
        assert "active_incidents" in result

    def test_components_have_string_values(self, service):
        components = service.get_system_status()["components"]
        assert all(isinstance(v, str) for v in components.values())


class TestCreateTicket:
    def test_returns_ticket_with_reference_id(self, service):
        result = service.create_ticket("user@example.com", "API broken", "Returns 500")
        assert re.match(r"BL-\d{5}", result["ticket_id"])

    def test_ticket_status_is_open(self, service):
        result = service.create_ticket("user@example.com", "subject", "desc")
        assert result["status"] == "open"

    def test_ticket_echoes_email_and_subject(self, service):
        result = service.create_ticket("user@example.com", "My subject", "desc")
        assert result["email"] == "user@example.com"
        assert result["subject"] == "My subject"

    def test_each_ticket_gets_unique_id(self, service):
        ids = {
            service.create_ticket("u@x.com", "s", "d")["ticket_id"] for _ in range(20)
        }
        assert len(ids) > 1


class TestGetTicket:
    def test_known_ticket_returns_details(self, service):
        result = service.get_ticket("BL-10001")
        assert result is not None
        assert "status" in result
        assert "subject" in result

    def test_lookup_is_case_insensitive(self, service):
        assert service.get_ticket("bl-10001") is not None

    def test_unknown_ticket_returns_none(self, service):
        assert service.get_ticket("BL-99999") is None


class TestSearchKnowledgeBase:
    def test_relevant_query_returns_articles(self, service):
        results = service.search_knowledge_base("webhook setup")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_articles_have_required_fields(self, service):
        for article in service.search_knowledge_base("api authentication"):
            assert "title" in article
            assert "summary" in article

    def test_unrelated_query_returns_empty_list(self, service):
        assert service.search_knowledge_base("xyzzy foobar qux") == []

    def test_returns_at_most_three_articles(self, service):
        results = service.search_knowledge_base("api integration webhook")
        assert len(results) <= 3
