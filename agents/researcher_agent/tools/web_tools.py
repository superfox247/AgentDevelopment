"""Web-related tools for the researcher agent.

Custom tools live here. The agent also uses google_search from google.adk.tools.
"""


def format_search_query(query: str) -> str:
    """Normalize a search query for better web results.

    Trims whitespace, collapses internal spaces, and strips common
    filler phrases. Use this to clean user queries before searching.

    Args:
        query: Raw search query from user or agent.

    Returns:
        Normalized query string.
    """
    if not query or not isinstance(query, str):
        return ""
    t = query.strip()
    while "  " in t:
        t = t.replace("  ", " ")
    for phrase in ("can you ", "please ", "i want to know ", "tell me "):
        if t.lower().startswith(phrase):
            t = t[len(phrase) :].strip()
            break
    return t
