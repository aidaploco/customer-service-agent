from unittest.mock import MagicMock, patch


from agent.billing.tools import (
    _cancel_subscription,
    _fmt_date,
    _get_invoice_history,
    _get_subscription,
    _request_refund,
    _update_plan,
)


def _mock_service(**attrs) -> MagicMock:
    svc = MagicMock()
    for k, v in attrs.items():
        setattr(svc, k, v)
    return svc


# _fmt_date


def test_fmt_date_formats_correctly():
    assert _fmt_date("2026-06-01") == "June 1, 2026"


def test_fmt_date_single_digit_day():
    assert _fmt_date("2026-01-05") == "January 5, 2026"


# _get_subscription


def test_get_subscription_found():
    data = {
        "plan": "Pro",
        "seats": 15,
        "amount_usd": 149,
        "renewal_date": "2026-06-01",
        "status": "active",
    }
    svc = _mock_service(get_subscription=MagicMock(return_value=data))
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _get_subscription("alice@example.com")
    assert "Pro" in result
    assert "15" in result
    assert "June 1, 2026" in result
    assert "Active" in result


def test_get_subscription_not_found():
    svc = _mock_service(get_subscription=MagicMock(return_value=None))
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _get_subscription("nobody@example.com")
    assert "No account found" in result


# _get_invoice_history


def test_get_invoice_history_found():
    data = [
        {"id": "INV-001", "date": "2026-05-01", "amount_usd": 149, "status": "paid"},
        {"id": "INV-002", "date": "2026-04-01", "amount_usd": 149, "status": "paid"},
    ]
    svc = _mock_service(get_invoices=MagicMock(return_value=data))
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _get_invoice_history("alice@example.com")
    assert "INV-001" in result
    assert "INV-002" in result
    assert "Paid" in result


def test_get_invoice_history_not_found():
    svc = _mock_service(get_invoices=MagicMock(return_value=None))
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _get_invoice_history("nobody@example.com")
    assert "No account found" in result


def test_get_invoice_history_empty():
    svc = _mock_service(get_invoices=MagicMock(return_value=[]))
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _get_invoice_history("alice@example.com")
    assert "No invoices found" in result


# _update_plan


def test_update_plan_success():
    svc = MagicMock()
    svc.valid_plans = ["Starter", "Pro", "Business", "Enterprise"]
    svc.update_plan.return_value = {
        "previous_plan": "Starter",
        "new_plan": "Pro",
        "effective": "immediately",
    }
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _update_plan("alice@example.com", "Pro")
    assert "Starter" in result
    assert "Pro" in result


def test_update_plan_not_found():
    svc = MagicMock()
    svc.valid_plans = ["Starter", "Pro", "Business", "Enterprise"]
    svc.update_plan.return_value = None
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _update_plan("nobody@example.com", "Pro")
    assert "No account found" in result


def test_update_plan_invalid_plan():
    svc = MagicMock()
    svc.valid_plans = ["Starter", "Pro", "Business", "Enterprise"]
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _update_plan("alice@example.com", "Gold")
    assert "not a valid plan" in result
    assert "Gold" in result


def test_update_plan_already_on_plan():
    svc = MagicMock()
    svc.valid_plans = ["Starter", "Pro", "Business", "Enterprise"]
    svc.update_plan.return_value = {
        "previous_plan": "Pro",
        "new_plan": "Pro",
        "effective": "immediately",
    }
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _update_plan("alice@example.com", "Pro")
    assert "already on the Pro plan" in result


# _request_refund


def test_request_refund_success():
    data = {
        "refund_request_id": "REF-INV-001",
        "invoice_id": "INV-001",
        "amount_usd": 149,
        "reason": "duplicate",
    }
    svc = _mock_service(request_refund=MagicMock(return_value=data))
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _request_refund("alice@example.com", "INV-001", "duplicate")
    assert "REF-INV-001" in result
    assert "149" in result
    assert "duplicate" in result


def test_request_refund_not_found():
    svc = _mock_service(request_refund=MagicMock(return_value=None))
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _request_refund("alice@example.com", "INV-999", "error")
    assert "not found" in result


# _cancel_subscription


def test_cancel_subscription_success():
    data = {"plan": "Pro", "access_until": "2026-06-01"}
    svc = _mock_service(cancel_subscription=MagicMock(return_value=data))
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _cancel_subscription("alice@example.com", "switching providers")
    assert "Pro" in result
    assert "June 1, 2026" in result


def test_cancel_subscription_not_found():
    svc = _mock_service(cancel_subscription=MagicMock(return_value=None))
    with patch("agent.billing.tools.get_billing_service", return_value=svc):
        result = _cancel_subscription("nobody@example.com", "reason")
    assert "No account found" in result
