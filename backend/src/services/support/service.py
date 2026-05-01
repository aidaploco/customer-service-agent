import random
from functools import lru_cache

from services.support import mock_data


class SupportService:
    """
    Handles all support data access and business logic.
    Currently backed by mock data; swap the data source here when a real API exists.
    """

    def get_system_status(self) -> dict:
        """Return current system status and active incidents."""
        return mock_data.SYSTEM_STATUS

    def create_ticket(self, email: str, subject: str, description: str) -> dict:
        """Create a support ticket and return its details including a reference ID."""
        ticket_id = f"BL-{random.randint(10000, 99999)}"
        return {
            "ticket_id": ticket_id,
            "email": email,
            "subject": subject,
            "status": "open",
        }

    def get_ticket(self, ticket_id: str) -> dict | None:
        """Return ticket details, or None if not found."""
        return mock_data.TICKETS.get(ticket_id.upper())

    def search_knowledge_base(self, query: str) -> list[dict]:
        """
        Return up to 3 knowledge base articles relevant to the query.
        Currently uses keyword matching; replace with vector search for production.
        """
        query_lower = query.lower()
        matches = [
            article
            for article in mock_data.KB_ARTICLES
            if any(tag in query_lower for tag in article["tags"])
            or any(word in article["title"].lower() for word in query_lower.split())
        ]
        return matches[:3]


@lru_cache(maxsize=1)
def get_support_service() -> SupportService:
    """Return the cached SupportService singleton."""
    return SupportService()
