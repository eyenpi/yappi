from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    sessionId: str  # New field for session management
