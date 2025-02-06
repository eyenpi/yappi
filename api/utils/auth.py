from fastapi import HTTPException, Security, Header
from fastapi.security import HTTPBearer
from api.config.settings import settings
import requests
from api.db.supabase_client import supabase

security = HTTPBearer()


def get_spotify_token() -> str:
    """Get Spotify API access token"""
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET,
        },
    )
    return response.json().get("access_token", "")


async def verify_supabase_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token provided")

    try:
        # Get token from Bearer header
        token = authorization.split(" ")[1]

        # Verify the token
        user = supabase.auth.get_user(token)

        # Return both user data and token for database operations
        return {"id": user.user.id, "access_token": token}
    except Exception as e:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
