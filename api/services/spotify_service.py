import requests
from api.config.settings import settings
from api.utils.auth import get_spotify_token
from typing_extensions import Annotated
from pydantic import Field


class SpotifyService:
    @staticmethod
    def search_spotify(
        q: Annotated[str, Field(description="The search query for finding music")],
        search_type: Annotated[
            str, Field(description="Type of search: 'track', 'artist', or 'album'")
        ],
        market: str = "US",
        limit: int = 2,
        offset: int = 0,
    ) -> str:
        """Search Spotify with given parameters"""
        access_token = get_spotify_token()
        url = f"{settings.SPOTIFY_API_BASE_URL}/search"

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "q": q,
                    "type": search_type,
                    "market": market,
                    "limit": limit,
                    "offset": offset,
                },
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Failed to fetch results from Spotify"}
