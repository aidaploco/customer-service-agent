from agents import function_tool


@function_tool
def greet(text: str) -> str:
    """
    Send a text response to the customer without routing them anywhere.
    Use this for the opening greeting, the introduction, and clarifying questions.
    """
    return text
