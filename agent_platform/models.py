from pydantic import BaseModel, Field

"""
Common data models used across the Agent Platform.

Defines Pydantic models for API requests, responses, and shared data structures
that do not belong to a specific domain.
"""


class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    message: str = Field(..., description="The user's message text.")
    user_id: str = Field("default_user", description="The ID of the user sending the message.")
    session_id: str = Field("default_session", description="The ID of the conversation session.")


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    score: float = Field(..., description="The feedback score (e.g. 0.0 to 1.0).")
    text: str | None = Field(None, description="Optional text comment.")
    run_id: str | None = Field(None, description="The ID of the run being rated.")
    user_id: str | None = Field(None, description="The user providing the feedback.")
