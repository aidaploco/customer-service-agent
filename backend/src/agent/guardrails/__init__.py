def _last_user_message(input: str | list) -> str:
    """Extract the last user message text from a str-or-list SDK input."""
    if isinstance(input, str):
        return input
    for item in reversed(input):
        if isinstance(item, dict) and item.get("role") == "user":
            content = item.get("content", "")
            return content if isinstance(content, str) else ""
    return ""
