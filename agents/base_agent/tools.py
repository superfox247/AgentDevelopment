"""
Example tool definition for Base Agent.
"""

from google.adk.tools import tool


@tool
def example_tool(name: str) -> str:
    """An example tool that greets the user.

    Args:
        name: The name of the person to greet.

    Returns:
        A greeting string.
    """
    return f"Hello, {name}!"
