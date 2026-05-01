"""
Mock data standing in for a real support API and knowledge base.
Replace this module's contents with real service calls when the backend exists.
"""

SYSTEM_STATUS: dict = {
    "overall": "operational",
    "components": {
        "API": "operational",
        "Dashboard": "operational",
        "Webhooks": "degraded_performance",
        "Reporting": "operational",
        "Integrations": "operational",
    },
    "active_incidents": [
        {
            "id": "INC-2026-012",
            "title": "Webhook delivery delays",
            "started": "2026-05-01T09:15:00Z",
            "severity": "minor",
            "update": "Our team is investigating increased latency in webhook delivery. Other services are unaffected.",
        }
    ],
}

TICKETS: dict[str, dict] = {
    "BL-10001": {
        "subject": "API rate limiting issue",
        "status": "in_progress",
        "created": "2026-04-28",
        "assigned_to": "Tier 2 Support",
    },
    "BL-10002": {
        "subject": "Webhook configuration question",
        "status": "resolved",
        "created": "2026-04-25",
        "resolution": "Webhook endpoint URL was missing the trailing slash. Updated and confirmed working.",
    },
}

KB_ARTICLES: list[dict] = [
    {
        "title": "Getting started with the Brightloop API",
        "summary": "How to authenticate, make your first API request, and understand rate limits.",
        "tags": ["api", "authentication", "rate limit", "getting started"],
    },
    {
        "title": "Setting up and troubleshooting webhooks",
        "summary": "How to configure webhook endpoints, verify signatures, and debug delivery failures.",
        "tags": ["webhook", "integration", "delivery", "signature", "debug"],
    },
    {
        "title": "Managing team members and roles",
        "summary": "How to invite users, assign roles (Member, Admin, Billing Contact), and remove access.",
        "tags": ["team", "users", "roles", "permissions", "invite"],
    },
    {
        "title": "Exporting project data",
        "summary": "How to export tasks, timelines, and reports in CSV or JSON format.",
        "tags": ["export", "data", "csv", "json", "report"],
    },
    {
        "title": "Connecting third-party integrations",
        "summary": "Step-by-step guides for Slack, Jira, GitHub, and Zapier integrations.",
        "tags": ["integration", "slack", "jira", "github", "zapier"],
    },
    {
        "title": "Understanding your Brightloop subscription",
        "summary": "Plan comparison, seat management, and how billing cycles work.",
        "tags": ["billing", "subscription", "plan", "seats", "pricing"],
    },
]
