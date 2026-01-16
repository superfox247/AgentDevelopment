
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    session_id: str = "default_session"

class FeedbackRequest(BaseModel):
    score: float
    text: str | None = None
    run_id: str | None = None
    user_id: str | None = None
