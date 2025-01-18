from pydantic import BaseModel, Field
from typing import Optional

class SearchSpotifyArgs(BaseModel):
    q: str = Field(..., description="The search query.")
    search_type: str = Field(..., description="Type: 'track', 'artist', 'album'.")
    market: Optional[str] = Field("US", description="Market code.")
    limit: Optional[int] = Field(2, description="Max results.")
    offset: Optional[int] = Field(0, description="First result index.")

class ChatRequest(BaseModel):
    task: str = Field(..., description="Chat input task.")