from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class UserThread(BaseModel):
    id: UUID = uuid4()  # Default to new UUID if not provided
    user_id: str
    api_id: str
    assistant_id: str
    thread_id: str
    created_at: datetime = datetime.utcnow()  # Set default to current UTC time
