import yaml
from pathlib import Path
import requests
from functools import wraps
from api.config.settings import settings
from api.utils.auth import get_spotify_token
from typing_extensions import Annotated
from pydantic import Field
from typing import Dict, Any, List, Union
import json

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
    def _filter_response(response: Dict[Any, Any], fields: str) -> Dict[Any, Any]:
        def extract_fields(data, field_list):
            if isinstance(data, dict):
                filtered_data = {}
                field_map = {}

                for field in field_list:
                    keys = field.split(".", 1)
                    if len(keys) == 2:
                        if keys[0] not in field_map:
                            field_map[keys[0]] = []
                        field_map[keys[0]].append(keys[1])
                    else:
                        filtered_data[field] = data.get(field)

                for key, sub_fields in field_map.items():
                    if key in data:
                        filtered_data[key] = extract_fields(data[key], sub_fields)

                return filtered_data
            elif isinstance(data, list):
                return [extract_fields(item, field_list) for item in data]
            return data

        field_list = fields.split(",")
        return extract_fields(response, field_list)

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
        fields: Annotated[
            str, Field(description=SPOTIFY_DOCS["search_spotify"]["params"]["fields"])
        ] = None,
        market: str = "US",
        limit: Annotated[
            int, Field(description=SPOTIFY_DOCS["search_spotify"]["params"]["limit"])
        ] = 1,
        offset: int = 0,
    ) -> dict:
        """Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes or audiobooks."""
        params = {
            "q": q,
            "type": search_type,
            "market": market,
            "limit": limit,
            "offset": offset,
        }
        response = SpotifyService._make_request("search", params)
        return SpotifyService._filter_response(response, fields)

    @staticmethod
    @with_yaml_doc("get_track")
    def get_track(
        fields: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_track"]["params"]["fields"])
        ],
        id: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_track"]["params"]["id"])
        ],
        market: str = "US",
    ) -> str:
        params = {"market": market}
        response = SpotifyService._make_request(f"tracks/{id}", params)
        return SpotifyService._filter_response(response, fields)

    @staticmethod
    @with_yaml_doc("get_artists_top_tracks")
    def get_artists_top_tracks(
        fields: Annotated[
            str,
            Field(
                description=SPOTIFY_DOCS["get_artists_top_tracks"]["params"]["fields"]
            ),
        ],
        id: Annotated[
            str,
            Field(description=SPOTIFY_DOCS["get_artists_top_tracks"]["params"]["id"]),
        ],
        market: str = "US",
    ) -> str:
        params = {"market": market}
        resonse = SpotifyService._make_request(f"artists/{id}/top-tracks", params)
        return SpotifyService._filter_response(resonse, fields)

    @staticmethod
    @with_yaml_doc("get_artist")
    def get_artist(
        fields: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_artist"]["params"]["fields"])
        ],
        id: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_artist"]["params"]["id"])
        ],
    ) -> str:
        response = SpotifyService._make_request(f"artists/{id}")
        return SpotifyService._filter_response(response, fields)

    @staticmethod
    @with_yaml_doc("get_artists_albums")
    def get_artists_albums(
        fields: Annotated[
            str,
            Field(description=SPOTIFY_DOCS["get_artists_albums"]["params"]["fields"]),
        ],
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
        response = SpotifyService._make_request(f"artists/{id}/albums", params)
        return SpotifyService._filter_response(response, fields)

    @staticmethod
    @with_yaml_doc("get_album")
    def get_album(
        fields: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_album"]["params"]["fields"])
        ],
        id: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_album"]["params"]["id"])
        ],
        market: str = "US",
    ) -> str:
        params = {"market": market}
        response = SpotifyService._make_request(f"albums/{id}", params)
        return SpotifyService._filter_response(response, fields)

    @staticmethod
    @with_yaml_doc("get_album_tracks")
    def get_album_tracks(
        fields: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_album_tracks"]["params"]["fields"])
        ],
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
        response = SpotifyService._make_request(f"albums/{id}/tracks", params)
        return SpotifyService._filter_response(response, fields)

    @staticmethod
    @with_yaml_doc("get_new_releases")
    def get_new_releases(
        fields: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_new_releases"]["params"]["fields"])
        ],
        limit: Annotated[
            int, Field(description=SPOTIFY_DOCS["get_new_releases"]["params"]["limit"])
        ] = 5,
        offset: int = 0,
    ) -> str:
        params = {"limit": limit, "offset": offset}
        response = SpotifyService._make_request("browse/new-releases", params)
        return SpotifyService._filter_response(response, fields)

    @staticmethod
    @with_yaml_doc("get_playlist")
    def get_playlist(
        fields: Annotated[
            str, Field(description=SPOTIFY_DOCS["get_playlist"]["params"]["fields"])
        ],
        playlist_id: Annotated[
            str,
            Field(description=SPOTIFY_DOCS["get_playlist"]["params"]["playlist_id"]),
        ],
        additional_types: Annotated[
            str,
            Field(
                description=SPOTIFY_DOCS["get_playlist"]["params"]["additional_types"]
            ),
        ] = None,
        market: str = "US",
    ) -> str:
        params = {"market": market}
        if additional_types:
            params["additional_types"] = additional_types
        response = SpotifyService._make_request(f"playlists/{playlist_id}", params)
        return SpotifyService._filter_response(response, fields)
