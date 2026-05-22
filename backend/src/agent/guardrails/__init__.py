def _last_user_message(input: str | list) -> str:
    """Extract the last user message text from a str-or-list SDK input."""
    if isinstance(input, str):
        return input
    for item in reversed(input):
        if isinstance(item, dict) and item.get("role") == "user":
            content = item.get("content", "")
            return content if isinstance(content, str) else ""
    return ""


def _conversation_context(input: str | list, max_turns: int = 4) -> tuple[str, str]:
    """Return (conversation_snippet, last_user_message) for context-aware guardrails.

    conversation_snippet contains the last max_turns exchanges formatted as plain text,
    so the guardrail LLM can evaluate the final message in context.
    """
    if isinstance(input, str):
        return "", input

    messages = [
        m
        for m in input
        if isinstance(m, dict)
        and m.get("role") in ("user", "assistant")
        and isinstance(m.get("content", ""), str)
        and m.get("content", "")
    ]

    recent = messages[-(max_turns * 2) :]
    if not recent:
        return "", ""

    last_user = next(
        (m["content"] for m in reversed(recent) if m["role"] == "user"), ""
    )

    lines = []
    for m in recent:
        label = "User" if m["role"] == "user" else "Agent"
        lines.append(f"{label}: {m['content']}")

    return "\n".join(lines), last_user
