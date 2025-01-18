from fastapi import APIRouter, HTTPException
from src.models.chat_models import ChatRequest
from src.services.chat_service import ChatService

router = APIRouter()

@router.post("/chat/{service}/ask")
async def chat_with_service(service: str, request: ChatRequest):
    """
    Handles chat requests for a specified service (e.g., Spotify).
    """
    if service.lower() == "spotify":
        response = await ChatService.handle_spotify_chat(request.task)
    else:
        raise HTTPException(status_code=400, detail="Unsupported service.")
    return {"response": response}