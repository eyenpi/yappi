import requests
from src.config.settings import settings

def get_spotify_token():
    """Authenticate with Spotify API and return an access token."""
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token", "")