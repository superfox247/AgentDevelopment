"""
Image Generator Server Entrypoint.

Exposes the Image Generator agent as a FastAPI/A2A service.
"""

from agent_platform.server import create_platform_app

from .agent import app as adk_app

# Create Standard App
app = create_platform_app(
    adk_app=adk_app, description="Generates images for course content.", enable_a2a=True
)

if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
