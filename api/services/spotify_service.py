import requests
import json
from api.config.settings import settings
from api.utils.auth import get_spotify_token
from api.models.chat_models import SearchSpotifyArgs
from api.utils.logger import get_logger

logger = get_logger(__name__)  # Initialize logger


class SpotifyService:
    @staticmethod
    def search_spotify(args: SearchSpotifyArgs) -> str:
        if isinstance(args, dict):
            args = SearchSpotifyArgs(**args)  # Convert dictionary to Pydantic model
        access_token = get_spotify_token()
        url = f"{settings.SPOTIFY_API_BASE_URL}/search"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "q": args.q,
            "type": args.search_type,
            "market": args.market,
            "limit": args.limit,
            "offset": args.offset,
        }

        logger.info(f"Searching Spotify: {params}")

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for non-200 status codes
            logger.info("Spotify API call successful")
            return json.dumps(response.json(), indent=2)
        except requests.exceptions.RequestException as e:
            logger.error(f"Spotify API error: {e}")
            return json.dumps({"error": "Failed to fetch results from Spotify"})
