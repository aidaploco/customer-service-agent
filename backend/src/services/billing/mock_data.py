"""
Mock data standing in for a real billing API.
Replace this module's contents with real service calls when the backend exists.
"""

from datetime import date

PLANS: list[str] = ["Starter", "Pro", "Business", "Enterprise"]


def _month(offset: int, day: int = 1) -> str:
    """ISO date `offset` months from the current one, so the mock data never goes stale."""
    index = date.today().year * 12 + date.today().month - 1 + offset
    return date(index // 12, index % 12 + 1, day).isoformat()


SUBSCRIPTIONS: dict[str, dict] = {
    "alice@example.com": {
        "plan": "Pro",
        "seats": 15,
        "amount_usd": 149,
        "renewal_date": _month(1),
        "status": "active",
    },
    "bob@example.org": {
        "plan": "Starter",
        "seats": 3,
        "amount_usd": 49,
        "renewal_date": _month(1, 15),
        "status": "active",
    },
    "carol@example.net": {
        "plan": "Business",
        "seats": 80,
        "amount_usd": 399,
        "renewal_date": _month(2, 10),
        "status": "active",
    },
}

INVOICES: dict[str, list[dict]] = {
    "alice@example.com": [
        {
            "id": "INV-2026-004",
            "date": _month(0),
            "amount_usd": 149,
            "status": "paid",
        },
        {
            "id": "INV-2026-003",
            "date": _month(-1),
            "amount_usd": 149,
            "status": "paid",
        },
        {
            "id": "INV-2026-002",
            "date": _month(-2),
            "amount_usd": 149,
            "status": "paid",
        },
    ],
    "bob@example.org": [
        {
            "id": "INV-2026-005",
            "date": _month(0),
            "amount_usd": 49,
            "status": "paid",
        },
        {
            "id": "INV-2026-001",
            "date": _month(-1),
            "amount_usd": 49,
            "status": "paid",
        },
    ],
    "carol@example.net": [
        {
            "id": "INV-2026-006",
            "date": _month(0),
            "amount_usd": 399,
            "status": "paid",
        },
        {
            "id": "INV-2026-007",
            "date": _month(-1),
            "amount_usd": 399,
            "status": "paid",
        },
    ],
}
