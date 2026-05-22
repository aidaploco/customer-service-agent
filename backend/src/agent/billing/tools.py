from datetime import datetime

from agents import function_tool

from services.billing.service import get_billing_service


def _fmt_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


def _get_subscription(email: str) -> str:
    data = get_billing_service().get_subscription(email)
    if data is None:
        return f"No account found for {email}. Please double-check the email address."
    return (
        f"Here are your subscription details:\n\n"
        f"• Plan: {data['plan']}\n"
        f"• Seats: {data['seats']}\n"
        f"• Amount: ${data['amount_usd']}/month\n"
        f"• Renewal date: {_fmt_date(data['renewal_date'])}\n"
        f"• Status: {data['status'].capitalize()}"
    )


def _get_invoice_history(email: str) -> str:
    data = get_billing_service().get_invoices(email)
    if data is None:
        return f"No account found for {email}. Please double-check the email address."
    if not data:
        return "No invoices found for this account."
    lines = "\n".join(
        f"• {inv['id']} — {_fmt_date(inv['date'])} — ${inv['amount_usd']} — {inv['status'].capitalize()}"
        for inv in data
    )
    return f"Here are your recent invoices:\n\n{lines}"


def _update_plan(email: str, new_plan: str) -> str:
    service = get_billing_service()
    if new_plan not in service.valid_plans:
        return f"'{new_plan}' is not a valid plan. Available plans: {', '.join(service.valid_plans)}."
    data = service.update_plan(email, new_plan)
    if data is None:
        return f"No account found for {email}. Please double-check the email address."
    if data["previous_plan"] == new_plan:
        return f"Your account is already on the {new_plan} plan."
    return (
        f"Your plan has been updated from {data['previous_plan']} to {data['new_plan']}, "
        f"effective {data['effective']}."
    )


def _request_refund(email: str, invoice_id: str, reason: str) -> str:
    data = get_billing_service().request_refund(email, invoice_id, reason)
    if data is None:
        return f"Invoice {invoice_id} not found for {email}. Please double-check the details."
    return (
        f"Your refund request has been submitted.\n\n"
        f"• Request ID: {data['refund_request_id']}\n"
        f"• Invoice: {data['invoice_id']}\n"
        f"• Amount: ${data['amount_usd']}\n"
        f"• Reason: {data['reason']}"
    )


def _cancel_subscription(email: str, reason: str) -> str:
    data = get_billing_service().cancel_subscription(email, reason)
    if data is None:
        return f"No account found for {email}. Please double-check the email address."
    return (
        f"Your {data['plan']} subscription has been scheduled for cancellation. "
        f"You'll retain full access until {_fmt_date(data['access_until'])}."
    )


@function_tool
def get_subscription(email: str) -> str:
    """Get the current subscription details for the account registered under the given email."""
    return _get_subscription(email)


@function_tool
def get_invoice_history(email: str) -> str:
    """Get the invoice history for the account registered under the given email."""
    return _get_invoice_history(email)


@function_tool
def update_plan(email: str, new_plan: str) -> str:
    """
    Upgrade or downgrade the subscription plan for the given account.
    Valid plans are: Starter, Pro, Business, Enterprise.
    """
    return _update_plan(email, new_plan)


@function_tool
def request_refund(email: str, invoice_id: str, reason: str) -> str:
    """Submit a refund request for a specific invoice."""
    return _request_refund(email, invoice_id, reason)


@function_tool
def cancel_subscription(email: str, reason: str) -> str:
    """Initiate the cancellation process for the given account."""
    return _cancel_subscription(email, reason)
