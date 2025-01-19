from fastapi import APIRouter, HTTPException, Depends, Security
from api.models.chat_models import ChatRequest
from api.services.chat_service import ChatService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import logging
from api.config.settings import Settings

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Load Supabase URL & Key from Environment Variables
SUPABASE_URL = Settings.NEXT_PUBLIC_SUPABASE_URL
SUPABASE_KEY = Settings.NEXT_PUBLIC_SUPABASE_ANON_KEY

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase URL or API Key is not set in environment variables.")

SUPABASE_AUTH_URL = f"{SUPABASE_URL}/auth/v1/user"

security = HTTPBearer()  # Bearer token security


async def verify_supabase_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """
    Verifies the Supabase JWT token by making a request to Supabase Auth API.
    """
    token = credentials.credentials
    if not token:
        logger.error("Missing Authorization token")
        raise HTTPException(status_code=401, detail="Missing Authorization token")

    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": str(SUPABASE_KEY),  # Ensure it's a string
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(SUPABASE_AUTH_URL, headers=headers)

        if response.status_code != 200:
            logger.error(
                f"Supabase token verification failed: {response.status_code} - {response.text}"
            )
            raise HTTPException(status_code=401, detail="Invalid Supabase token")

        return response.json()  # Return user info if token is valid

    except httpx.RequestError as e:
        logger.error(f"Error verifying Supabase token: {e}")
        raise HTTPException(
            status_code=503, detail="Authentication service unavailable."
        )


@router.post("/chat/{service}/ask")
async def chat_with_service(
    service: str,
    request: ChatRequest,
    user_data=Depends(verify_supabase_token),
):
    """
    Handles chat requests for a specified service (e.g., Spotify).
    """
    try:
        if service.lower() == "spotify":
            response = await ChatService.handle_spotify_chat(request.message)
        else:
            logger.warning(f"Unsupported service: {service}")
            raise HTTPException(status_code=400, detail="Unsupported service.")

        return {"response": response}

    except Exception as e:
        logger.error(f"Error handling chat request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
