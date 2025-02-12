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
    def _make_request(endpoint: str, params: dict = None) -> dict:
        """Helper method to make requests to Spotify API"""
        access_token = get_spotify_token()
        url = f"{settings.SPOTIFY_API_BASE_URL}/{endpoint}"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"error": "Failed to fetch data from Spotify"}

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
        params = {
            "q": q,
            "type": search_type,
            "market": market,
            "limit": limit,
            "offset": offset,
        }
        return SpotifyService._make_request("search", params)

    @staticmethod
    @with_yaml_doc("get_track")
    def get_track(
        id: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_track"]["params"]["id"])
        ],
        market: str = "US",
    ) -> str:
        params = {"market": market}
        return SpotifyService._make_request(f"tracks/{id}", params)

    @staticmethod
    @with_yaml_doc("get_artists_top_tracks")
    def get_artists_top_tracks(
        id: Annotated[
            str,
            Field(description=SPOTIFY_DOCS["get_artists_top_tracks"]["params"]["id"]),
        ],
        market: str = "US",
    ) -> str:
        params = {"market": market}
        return SpotifyService._make_request(f"artists/{id}/top-tracks", params)

    @staticmethod
    @with_yaml_doc("get_artist")
    def get_artist(
        id: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_artist"]["params"]["id"])
        ]
    ) -> str:
        return SpotifyService._make_request(f"artists/{id}")

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
        params = {"limit": limit, "market": market, "offset": offset}
        if include_groups:
            params["include_groups"] = include_groups
        return SpotifyService._make_request(f"artists/{id}/albums", params)

    @staticmethod
    @with_yaml_doc("get_album")
    def get_album(
        id: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_album"]["params"]["id"])
        ],
        market: str = "US",
    ) -> str:
        params = {"market": market}
        return SpotifyService._make_request(f"albums/{id}", params)

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
        params = {"limit": limit, "market": market, "offset": offset}
        return SpotifyService._make_request(f"albums/{id}/tracks", params)

    @staticmethod
    @with_yaml_doc("get_new_releases")
    def get_new_releases(
        limit: Annotated[
            int, Field(description=SPOTIFY_DOCS["get_new_releases"]["params"]["limit"])
        ] = 5,
        offset: int = 0,
    ) -> str:
        params = {"limit": limit, "offset": offset}
        return SpotifyService._make_request("browse/new-releases", params)

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
        params = {}
        if fields:
            params["fields"] = fields
        if additional_types:
            params["additional_types"] = additional_types
        params["market"] = market
        return SpotifyService._make_request(f"playlists/{playlist_id}", params)
