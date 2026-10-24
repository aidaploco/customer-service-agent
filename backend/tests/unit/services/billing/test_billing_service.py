import pytest

from services.billing.service import BillingService

_KNOWN_EMAIL = "alice@example.com"
_UNKNOWN_EMAIL = "nobody@unknown.com"


@pytest.fixture
def service() -> BillingService:
    return BillingService()


class TestGetSubscription:
    def test_returns_data_for_known_account(self, service):
        result = service.get_subscription(_KNOWN_EMAIL)
        assert result is not None
        assert result["plan"] == "Pro"
        assert "renewal_date" in result
        assert "amount_usd" in result

    def test_returns_none_for_unknown_account(self, service):
        assert service.get_subscription(_UNKNOWN_EMAIL) is None

    def test_email_lookup_is_case_insensitive(self, service):
        assert service.get_subscription(_KNOWN_EMAIL.upper()) is not None


class TestGetInvoices:
    def test_returns_list_for_known_account(self, service):
        result = service.get_invoices(_KNOWN_EMAIL)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_invoices_have_required_fields(self, service):
        for inv in service.get_invoices(_KNOWN_EMAIL):
            assert "id" in inv
            assert "date" in inv
            assert "amount_usd" in inv
            assert "status" in inv

    def test_returns_none_for_unknown_account(self, service):
        assert service.get_invoices(_UNKNOWN_EMAIL) is None


class TestUpdatePlan:
    def test_valid_plan_change_returns_result(self, service):
        result = service.update_plan(_KNOWN_EMAIL, "Business")
        assert result is not None
        assert result["status"] == "success"
        assert result["new_plan"] == "Business"
        assert result["previous_plan"] == "Pro"

    def test_invalid_plan_raises_value_error(self, service):
        with pytest.raises(ValueError, match="Invalid plan"):
            service.update_plan(_KNOWN_EMAIL, "InvalidPlan")

    def test_unknown_account_returns_none(self, service):
        assert service.update_plan(_UNKNOWN_EMAIL, "Pro") is None

    def test_valid_plans_property(self, service):
        assert "Starter" in service.valid_plans
        assert "Enterprise" in service.valid_plans


class TestRequestRefund:
    def test_valid_refund_returns_result(self, service):
        result = service.request_refund(_KNOWN_EMAIL, "INV-2026-004", "Charged twice")
        assert result is not None
        assert result["status"] == "submitted"
        assert result["invoice_id"] == "INV-2026-004"
        assert "refund_request_id" in result

    def test_unknown_invoice_returns_none(self, service):
        assert service.request_refund(_KNOWN_EMAIL, "INV-9999-999", "reason") is None

    def test_unknown_account_returns_none(self, service):
        assert service.request_refund(_UNKNOWN_EMAIL, "INV-2026-004", "reason") is None


class TestCancelSubscription:
    def test_returns_cancellation_result(self, service):
        result = service.cancel_subscription(_KNOWN_EMAIL, "Too expensive")
        assert result is not None
        assert result["status"] == "cancellation_scheduled"
        assert "access_until" in result
        assert result["reason_recorded"] == "Too expensive"

    def test_unknown_account_returns_none(self, service):
        assert service.cancel_subscription(_UNKNOWN_EMAIL, "reason") is None
