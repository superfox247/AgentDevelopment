"""Researcher agent: web-capable research assistant using ADK patterns."""

# Ensure config is loaded first to set up GOOGLE_API_KEY from GEMINI_API_KEY
# This must happen before agent.py imports google.adk.agents
try:
    import agent_platform.config  # noqa: F401
except ImportError:
    # If agent_platform is not available (e.g., when running directly with ADK),
    # set up the mapping manually
    import os
    from dotenv import load_dotenv
    load_dotenv(override=False)
    vertex_ai_setting = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").strip().lower()
    use_vertex_ai = vertex_ai_setting in ("true", "1", "yes")
    if not use_vertex_ai and not os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

from .agent import root_agent

__all__ = ["root_agent"]
