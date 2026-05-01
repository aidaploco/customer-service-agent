import json

from agents import function_tool

from services.billing.service import get_billing_service


@function_tool
def get_subscription(email: str) -> str:
    """Get the current subscription details for the account registered under the given email."""
    data = get_billing_service().get_subscription(email)
    if data is None:
        return f"No account found for {email}."
    return json.dumps(data)


@function_tool
def get_invoice_history(email: str) -> str:
    """Get the invoice history for the account registered under the given email."""
    data = get_billing_service().get_invoices(email)
    if data is None:
        return f"No account found for {email}."
    return json.dumps(data)


@function_tool
def update_plan(email: str, new_plan: str) -> str:
    """
    Upgrade or downgrade the subscription plan for the given account.
    Valid plans are: Starter, Pro, Business, Enterprise.
    """
    service = get_billing_service()
    if new_plan not in service.valid_plans:
        return f"Invalid plan '{new_plan}'. Valid options: {', '.join(service.valid_plans)}."
    data = service.update_plan(email, new_plan)
    if data is None:
        return f"No account found for {email}."
    if data["previous_plan"] == new_plan:
        return f"The account is already on the {new_plan} plan."
    return json.dumps(data)


@function_tool
def request_refund(email: str, invoice_id: str, reason: str) -> str:
    """Submit a refund request for a specific invoice."""
    data = get_billing_service().request_refund(email, invoice_id, reason)
    if data is None:
        return f"Invoice {invoice_id} not found for {email}."
    return json.dumps(data)


@function_tool
def cancel_subscription(email: str, reason: str) -> str:
    """Initiate the cancellation process for the given account."""
    data = get_billing_service().cancel_subscription(email, reason)
    if data is None:
        return f"No account found for {email}."
    return json.dumps(data)
