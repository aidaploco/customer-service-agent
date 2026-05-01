"""
Mock data standing in for a real billing API.
Replace this module's contents with real service calls when the backend exists.
"""

PLANS: list[str] = ["Starter", "Pro", "Business", "Enterprise"]

SUBSCRIPTIONS: dict[str, dict] = {
    "alice@acme.com": {
        "plan": "Pro",
        "seats": 15,
        "amount_usd": 149,
        "renewal_date": "2026-06-01",
        "status": "active",
    },
    "bob@startup.io": {
        "plan": "Starter",
        "seats": 3,
        "amount_usd": 49,
        "renewal_date": "2026-05-15",
        "status": "active",
    },
    "carol@enterprise.com": {
        "plan": "Business",
        "seats": 80,
        "amount_usd": 399,
        "renewal_date": "2026-07-10",
        "status": "active",
    },
}

INVOICES: dict[str, list[dict]] = {
    "alice@acme.com": [
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
    "bob@startup.io": [
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
    "carol@enterprise.com": [
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
