
# Note: Google ADK 1.23+ does not use a @tool decorator.
# Tools are defined as standard functions and registered via valid configuration or inspection.

def example_tool(name: str) -> str:
    """An example tool that greets the user.

    Args:
        name: The name of the person to greet.

    Returns:
        A greeting string.
    """
    return f"Hello, {name}!"
