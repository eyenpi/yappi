from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from api.config.settings import settings
import requests

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


async def verify_supabase_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Verify Supabase JWT token"""
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization token")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.NEXT_PUBLIC_SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {credentials.credentials}",
                    "apikey": str(settings.NEXT_PUBLIC_SUPABASE_ANON_KEY),
                },
            )

        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")

        return response.json()
    except httpx.RequestError:
        raise HTTPException(
            status_code=503, detail="Authentication service unavailable"
        )
