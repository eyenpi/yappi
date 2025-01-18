from fastapi import APIRouter, HTTPException
from api.models.chat_models import ChatRequest
from api.services.chat_service import ChatService

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
    return {"role": "assistant", "content": response}
