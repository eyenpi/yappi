from fastapi import APIRouter, HTTPException, Depends
from api.models.chat_models import ChatRequest
from api.services.chat_service import ChatService
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from api.config.settings import Settings

router = APIRouter()

# Load Supabase URL & Key from Environment Variables
SUPABASE_URL = Settings.NEXT_PUBLIC_SUPABASE_URL
SUPABASE_KEY = Settings.NEXT_PUBLIC_SUPABASE_ANON_KEY
SUPABASE_AUTH_URL = f"{SUPABASE_URL}/auth/v1/user"


security = HTTPBearer()  # Bearer token security


async def verify_supabase_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """
    Verifies the Supabase JWT token by making a request to Supabase Auth API.
    """
    token = credentials.credentials
    headers = {"Authorization": f"Bearer {token}", "apikey": SUPABASE_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(SUPABASE_AUTH_URL, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Supabase token")

    user_data = response.json()
    return user_data  # Return user info if token is valid


@router.post("/chat/{service}/ask")
async def chat_with_service(
    service: str,
    request: ChatRequest,
    response=Depends(verify_supabase_token),
):
    """
    Handles chat requests for a specified service (e.g., Spotify).
    """
    if service.lower() == "spotify":
        response = await ChatService.handle_spotify_chat(request.message)
    else:
        raise HTTPException(status_code=400, detail="Unsupported service.")
    return {"response": response}
