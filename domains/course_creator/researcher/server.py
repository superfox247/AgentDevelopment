from agent_platform.server import create_platform_app

"""
Researcher Server Entrypoint.

Exposes the Researcher agent as a FastAPI/A2A service.
"""

from .agent import app as adk_app

# Create Standard App
app = create_platform_app(
    adk_app=adk_app,
    description="Gathers information using Google Search.",
    enable_a2a=True,
)

if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
