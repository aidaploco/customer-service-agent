from agents import function_tool

from services.support.service import get_support_service


def _get_system_status() -> str:
    data = get_support_service().get_system_status()
    overall = data["overall"].replace("_", " ").capitalize()
    lines = [f"Overall status: {overall}\n"]
    lines.append("Components:")
    for name, status in data["components"].items():
        lines.append(f"  • {name}: {status.replace('_', ' ').capitalize()}")
    incidents = data.get("active_incidents", [])
    if incidents:
        lines.append("\nActive incidents:")
        for inc in incidents:
            severity = inc["severity"].capitalize()
            lines.append(f"  • [{severity}] {inc['title']}")
            lines.append(f"    {inc['update']}")
    else:
        lines.append("\nNo active incidents.")
    return "\n".join(lines)


def _search_knowledge_base(query: str) -> str:
    results = get_support_service().search_knowledge_base(query)
    if not results:
        return "No knowledge base articles found for that query."
    lines = []
    for article in results:
        lines.append(f"**{article['title']}**")
        lines.append(article["summary"])
    return "\n\n".join(lines)


def _create_ticket(email: str, subject: str, description: str) -> str:
    data = get_support_service().create_ticket(email, subject, description)
    return (
        f"Your support ticket has been created.\n\n"
        f"• Ticket ID: {data['ticket_id']}\n"
        f"• Subject: {data['subject']}\n"
        f"• Status: {data['status'].capitalize()}\n\n"
        f"Our team will follow up at {data['email']}."
    )


def _get_ticket_status(ticket_id: str) -> str:
    data = get_support_service().get_ticket(ticket_id)
    if data is None:
        return f"No ticket found with ID {ticket_id.upper()}. Please check the reference number and try again."
    lines = [
        f"Ticket {ticket_id.upper()}:",
        f"• Subject: {data['subject']}",
        f"• Status: {data['status'].replace('_', ' ').capitalize()}",
        f"• Created: {data['created']}",
    ]
    if "assigned_to" in data:
        lines.append(f"• Assigned to: {data['assigned_to']}")
    if "resolution" in data:
        lines.append(f"• Resolution: {data['resolution']}")
    return "\n".join(lines)


@function_tool
def get_system_status() -> str:
    """Check the current Brightloop system status and any ongoing incidents."""
    return _get_system_status()


@function_tool
def search_knowledge_base(query: str) -> str:
    """
    Search the Brightloop knowledge base for documentation relevant to the customer's issue.
    Use this before creating a ticket to check if a self-service answer exists.
    """
    return _search_knowledge_base(query)


@function_tool
def create_ticket(email: str, subject: str, description: str) -> str:
    """
    Create a support ticket for an issue that could not be resolved in the conversation.
    Returns a unique ticket reference number.
    """
    return _create_ticket(email, subject, description)


@function_tool
def get_ticket_status(ticket_id: str) -> str:
    """Look up the status of an existing support ticket by its reference number (format: BL-XXXXX)."""
    return _get_ticket_status(ticket_id)
