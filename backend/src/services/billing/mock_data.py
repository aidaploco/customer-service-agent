"""
Mock data standing in for a real billing API.
Replace this module's contents with real service calls when the backend exists.
"""

PLANS: list[str] = ["Starter", "Pro", "Business", "Enterprise"]

SUBSCRIPTIONS: dict[str, dict] = {
    "alice@example.com": {
        "plan": "Pro",
        "seats": 15,
        "amount_usd": 149,
        "renewal_date": "2026-06-01",
        "status": "active",
    },
    "bob@example.org": {
        "plan": "Starter",
        "seats": 3,
        "amount_usd": 49,
        "renewal_date": "2026-05-15",
        "status": "active",
    },
    "carol@example.net": {
        "plan": "Business",
        "seats": 80,
        "amount_usd": 399,
        "renewal_date": "2026-07-10",
        "status": "active",
    },
}

INVOICES: dict[str, list[dict]] = {
    "alice@example.com": [
        {
            "id": "INV-2026-004",
            "date": "2026-05-01",
            "amount_usd": 149,
            "status": "paid",
        },
        {
            "id": "INV-2026-003",
            "date": "2026-04-01",
            "amount_usd": 149,
            "status": "paid",
        },
        {
            "id": "INV-2026-002",
            "date": "2026-03-01",
            "amount_usd": 149,
            "status": "paid",
        },
    ],
    "bob@example.org": [
        {
            "id": "INV-2026-005",
            "date": "2026-05-01",
            "amount_usd": 49,
            "status": "paid",
        },
        {
            "id": "INV-2026-001",
            "date": "2026-04-01",
            "amount_usd": 49,
            "status": "paid",
        },
    ],
    "carol@example.net": [
        {
            "id": "INV-2026-006",
            "date": "2026-05-01",
            "amount_usd": 399,
            "status": "paid",
        },
        {
            "id": "INV-2026-007",
            "date": "2026-04-01",
            "amount_usd": 399,
            "status": "paid",
        },
    ],
}
