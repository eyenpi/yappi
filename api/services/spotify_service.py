import yaml
from pathlib import Path
import requests
from functools import wraps
from api.config.settings import settings
from api.utils.auth import get_spotify_token
from typing_extensions import Annotated
from pydantic import Field

# Load documentation from YAML
docs_path = Path(__file__).parent.parent / "docs" / "spotify_docs.yaml"
with open(docs_path, "r") as f:
    SPOTIFY_DOCS = yaml.safe_load(f)


def with_yaml_doc(method_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Attach the documentation from YAML
        wrapper.yaml_doc = SPOTIFY_DOCS[method_name]["method_doc"]
        return wrapper

    return decorator


class SpotifyService:
    @staticmethod
    @with_yaml_doc("search_spotify")
    def search_spotify(
        q: Annotated[
            str, Field(description=SPOTIFY_DOCS["search_spotify"]["params"]["q"])
        ],
        search_type: Annotated[
            str,
            Field(description=SPOTIFY_DOCS["search_spotify"]["params"]["search_type"]),
        ],
        market: str = "US",
        limit: Annotated[
            int, Field(description=SPOTIFY_DOCS["search_spotify"]["params"]["limit"])
        ] = 1,
        offset: int = 0,
    ) -> str:
        """Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes or audiobooks."""
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

    @staticmethod
    @with_yaml_doc("get_track")
    def get_track(
        id: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_track"]["params"]["id"])
        ],
        market: str = "US",
    ) -> str:
        access_token = get_spotify_token()
        url = f"{settings.SPOTIFY_API_BASE_URL}/tracks/{id}"

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params={"market": market},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Failed to fetch track from Spotify"}

    @staticmethod
    @with_yaml_doc("get_artists_top_tracks")
    def get_artists_top_tracks(
        id: Annotated[
            str,
            Field(description=SPOTIFY_DOCS["get_artists_top_tracks"]["params"]["id"]),
        ],
        market: str = "US",
    ) -> str:
        access_token = get_spotify_token()
        url = f"{settings.SPOTIFY_API_BASE_URL}/artists/{id}/top-tracks"

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params={"market": market},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Failed to fetch artist's top tracks from Spotify"}

    @staticmethod
    @with_yaml_doc("get_artist")
    def get_artist(
        id: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_artist"]["params"]["id"])
        ]
    ) -> str:
        access_token = get_spotify_token()
        url = f"{settings.SPOTIFY_API_BASE_URL}/artists/{id}"

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Failed to fetch artist from Spotify"}

    @staticmethod
    @with_yaml_doc("get_artists_albums")
    def get_artists_albums(
        id: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_artists_albums"]["params"]["id"])
        ],
        include_groups: Annotated[
            str,
            Field(
                description=SPOTIFY_DOCS["get_artists_albums"]["params"][
                    "include_groups"
                ]
            ),
        ] = None,
        limit: Annotated[
            int,
            Field(description=SPOTIFY_DOCS["get_artists_albums"]["params"]["limit"]),
        ] = 1,
        market: str = "US",
        offset: int = 0,
    ) -> str:
        access_token = get_spotify_token()
        url = f"{settings.SPOTIFY_API_BASE_URL}/artists/{id}/albums"

        params = {"limit": limit, "market": market, "offset": offset}
        if include_groups:
            params["include_groups"] = include_groups

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Failed to fetch artist's albums from Spotify"}

    @staticmethod
    @with_yaml_doc("get_album")
    def get_album(
        id: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_album"]["params"]["id"])
        ],
        market: str = "US",
    ) -> str:
        access_token = get_spotify_token()
        url = f"{settings.SPOTIFY_API_BASE_URL}/albums/{id}"

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params={"market": market},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Failed to fetch album from Spotify"}

    @staticmethod
    @with_yaml_doc("get_album_tracks")
    def get_album_tracks(
        id: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_album_tracks"]["params"]["id"])
        ],
        limit: Annotated[
            int, Field(description=SPOTIFY_DOCS["get_album_tracks"]["params"]["limit"])
        ] = 1,
        market: str = "US",
        offset: int = 0,
    ) -> str:
        access_token = get_spotify_token()
        url = f"{settings.SPOTIFY_API_BASE_URL}/albums/{id}/tracks"

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params={"limit": limit, "market": market, "offset": offset},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Failed to fetch album tracks from Spotify"}

    @staticmethod
    @with_yaml_doc("get_new_releases")
    def get_new_releases(
        limit: Annotated[
            int, Field(description=SPOTIFY_DOCS["get_new_releases"]["params"]["limit"])
        ] = 5,
        offset: int = 0,
    ) -> str:
        access_token = get_spotify_token()
        url = f"{settings.SPOTIFY_API_BASE_URL}/browse/new-releases"

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params={"limit": limit, "offset": offset},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Failed to fetch new releases from Spotify"}

    @staticmethod
    @with_yaml_doc("get_playlist")
    def get_playlist(
        playlist_id: Annotated[
            str,
            Field(description=SPOTIFY_DOCS["get_playlist"]["params"]["playlist_id"]),
        ],
        fields: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_playlist"]["params"]["fields"])
        ] = None,
        additional_types: Annotated[
            str,
            Field(
                description=SPOTIFY_DOCS["get_playlist"]["params"]["additional_types"]
            ),
        ] = None,
        market: str = "US",
    ) -> str:
        access_token = get_spotify_token()
        url = f"{settings.SPOTIFY_API_BASE_URL}/playlists/{playlist_id}"

        params = {}
        if fields:
            params["fields"] = fields
        if additional_types:
            params["additional_types"] = additional_types
        params["market"] = market

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {access_token}"},
                params=params,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Failed to fetch playlist from Spotify"}
