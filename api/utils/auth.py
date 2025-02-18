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
    """Verify Supabase JWT token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token provided")

    # Validate Bearer token format
    if not authorization.startswith("Bearer ") or len(authorization.split()) != 2:
        raise HTTPException(
            status_code=401, detail="Invalid authorization header format"
        )

    try:
        # Get token from Bearer header
        token = authorization.split()[1]

        # Verify the token
        user = supabase.auth.get_user(token)

        # Return both user ID and token
        return {"id": user.user.id, "access_token": token}

    except supabase.GoTrueError as e:
        # Handle specific Supabase auth errors
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        # Log unexpected errors but don't expose details
        raise HTTPException(status_code=500, detail="Internal server error")
