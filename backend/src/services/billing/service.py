from functools import lru_cache

from services.billing import mock_data


class BillingService:
    """
    Handles all billing data access and business logic.
    Currently backed by mock data; swap the data source here when a real API exists.
    """

    @property
    def valid_plans(self) -> list[str]:
        return mock_data.PLANS

    def get_subscription(self, email: str) -> dict | None:
        """Return subscription details, or None if the account does not exist."""
        return mock_data.SUBSCRIPTIONS.get(email.lower())

    def get_invoices(self, email: str) -> list[dict] | None:
        """Return invoice history, or None if the account does not exist."""
        return mock_data.INVOICES.get(email.lower())

    def update_plan(self, email: str, new_plan: str) -> dict | None:
        """
        Change the subscription plan. Returns the result dict, or None if the
        account does not exist. Raises ValueError for an unrecognised plan name.
        """
        if new_plan not in mock_data.PLANS:
            raise ValueError(
                f"Invalid plan '{new_plan}'. Valid options: {', '.join(mock_data.PLANS)}."
            )
        sub = mock_data.SUBSCRIPTIONS.get(email.lower())
        if sub is None:
            return None
        return {
            "status": "success",
            "previous_plan": sub["plan"],
            "new_plan": new_plan,
            "effective": "immediately",
        }

    def request_refund(self, email: str, invoice_id: str, reason: str) -> dict | None:
        """
        Submit a refund request. Returns the result dict, or None if the invoice
        or account is not found.
        """
        invoices = mock_data.INVOICES.get(email.lower(), [])
        invoice = next((inv for inv in invoices if inv["id"] == invoice_id), None)
        if invoice is None:
            return None
        return {
            "status": "submitted",
            "refund_request_id": f"REF-{invoice_id}",
            "invoice_id": invoice_id,
            "amount_usd": invoice["amount_usd"],
            "reason": reason,
        }

    def cancel_subscription(self, email: str, reason: str) -> dict | None:
        """Initiate cancellation. Returns the result dict, or None if not found."""
        sub = mock_data.SUBSCRIPTIONS.get(email.lower())
        if sub is None:
            return None
        return {
            "status": "cancellation_scheduled",
            "plan": sub["plan"],
            "access_until": sub["renewal_date"],
            "reason_recorded": reason,
        }


@lru_cache(maxsize=1)
def get_billing_service() -> BillingService:
    """Return the cached BillingService singleton."""
    return BillingService()
