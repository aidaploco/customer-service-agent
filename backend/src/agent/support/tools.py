import json

from agents import function_tool

from services.support.service import get_support_service


@function_tool
def get_system_status() -> str:
    """Check the current Brightloop system status and any ongoing incidents."""
    return json.dumps(get_support_service().get_system_status())


@function_tool
def search_knowledge_base(query: str) -> str:
    """
    Search the Brightloop knowledge base for documentation relevant to the customer's issue.
    Use this before creating a ticket to check if a self-service answer exists.
    """
    results = get_support_service().search_knowledge_base(query)
    if not results:
        return "No knowledge base articles found for that query."
    return json.dumps(results)


@function_tool
def create_ticket(email: str, subject: str, description: str) -> str:
    """
    Create a support ticket for an issue that could not be resolved in the conversation.
    Returns a unique ticket reference number.
    """
    return json.dumps(get_support_service().create_ticket(email, subject, description))


@function_tool
def get_ticket_status(ticket_id: str) -> str:
    """Look up the status of an existing support ticket by its reference number (format: BL-XXXXX)."""
    data = get_support_service().get_ticket(ticket_id)
    if data is None:
        return f"No ticket found with ID {ticket_id}. Please check the reference number and try again."
    return json.dumps({"ticket_id": ticket_id.upper(), **data})
