import pytest
from unittest.mock import patch
from api.services.spotify_service import SpotifyService

MOCK_ALBUMS_RESPONSE = {
    "href": "https://api.spotify.com/v1/me/shows?offset=0&limit=20",
    "limit": 20,
    "next": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
    "offset": 0,
    "previous": "https://api.spotify.com/v1/me/shows?offset=1&limit=1",
    "total": 4,
    "items": [
        {
            "album_type": "compilation",
            "total_tracks": 9,
            "available_markets": ["CA", "BR", "IT"],
            "external_urls": {"spotify": "string"},
            "href": "string",
            "id": "2up3OPMp9Tb4dAKM2erWXQ",
            "images": [
                {
                    "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
                    "height": 300,
                    "width": 300,
                }
            ],
            "name": "string",
            "release_date": "1981-12",
            "release_date_precision": "year",
            "restrictions": {"reason": "market"},
            "type": "album",
            "uri": "spotify:album:2up3OPMp9Tb4dAKM2erWXQ",
            "artists": [
                {
                    "external_urls": {"spotify": "string"},
                    "href": "string",
                    "id": "string",
                    "name": "string",
                    "type": "artist",
                    "uri": "string",
                }
            ],
            "album_group": "compilation",
        }
    ],
}

MOCK_SEARCH_RESPONSE = {
    "tracks": {
        "href": "https://api.spotify.com/v1/me/shows?offset=0&limit=20",
        "items": [
            {
                "album": {
                    "album_type": "compilation",
                    "total_tracks": 9,
                    "name": "Album Name",
                    "release_date": "1981-12",
                    "id": "2up3OPMp9Tb4dAKM2erWXQ",
                },
                "artists": [
                    {
                        "id": "artist_id",
                        "name": "Artist Name",
                        "type": "artist",
                    }
                ],
                "duration_ms": 180000,
                "id": "track_id",
                "name": "Track Name",
                "popularity": 75,
                "preview_url": "https://preview.url",
            }
        ],
        "limit": 20,
        "total": 4,
    },
    "artists": {
        "items": [
            {
                "genres": ["Prog rock", "Grunge"],
                "id": "artist_id",
                "images": [
                    {
                        "url": "https://i.scdn.co/image/abc123",
                    }
                ],
                "name": "Artist Name",
                "popularity": 80,
            }
        ]
    },
    "albums": {
        "items": [
            {
                "album_type": "album",
                "id": "album_id",
                "name": "Album Name",
                "release_date": "1981-12",
                "total_tracks": 12,
                "artists": [
                    {
                        "name": "Artist Name",
                    }
                ],
            }
        ]
    },
}


class TestSpotifyService:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup the mock service before each test"""
        self.mock_response = MOCK_ALBUMS_RESPONSE
        self.patcher = patch(
            "api.services.spotify_service.SpotifyService._make_request"
        )
        self.mock_request = self.patcher.start()
        self.mock_request.return_value = self.mock_response
        yield
        self.patcher.stop()

    def test_get_artists_albums_basic_fields(self):
        """Test filtering with basic fields"""
        fields = "items.id,items.name,items.album_type,items.release_date"
        result = SpotifyService.get_artists_albums(fields=fields, id="test_id", limit=1)

        expected = {
            "items": [
                {
                    "id": "2up3OPMp9Tb4dAKM2erWXQ",
                    "name": "string",
                    "album_type": "compilation",
                    "release_date": "1981-12",
                }
            ],
        }
        assert result == expected

    def test_get_artists_albums_nested_fields(self):
        """Test filtering with nested fields"""
        fields = "items.name,items.artists.name,items.images.url,total"
        result = SpotifyService.get_artists_albums(fields=fields, id="test_id", limit=1)

        expected = {
            "items": [
                {
                    "name": "string",
                    "artists": [{"name": "string"}],
                    "images": [
                        {
                            "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228"
                        }
                    ],
                }
            ],
            "total": 4,
        }
        assert result == expected

    def test_get_artists_albums_full_details(self):
        """Test filtering with full details"""
        fields = (
            "items.id,items.name,items.album_type,items.release_date,"
            "items.total_tracks,items.artists.name,items.images.url,"
            "items.external_urls.spotify"
        )
        result = SpotifyService.get_artists_albums(fields=fields, id="test_id", limit=1)

        expected = {
            "items": [
                {
                    "id": "2up3OPMp9Tb4dAKM2erWXQ",
                    "name": "string",
                    "album_type": "compilation",
                    "release_date": "1981-12",
                    "total_tracks": 9,
                    "artists": [{"name": "string"}],
                    "images": [
                        {
                            "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228"
                        }
                    ],
                    "external_urls": {"spotify": "string"},
                }
            ],
        }
        assert result == expected


class TestSpotifySearch:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup the mock service before each test"""
        self.patcher = patch(
            "api.services.spotify_service.SpotifyService._make_request"
        )
        self.mock_request = self.patcher.start()
        self.mock_request.return_value = MOCK_SEARCH_RESPONSE
        yield
        self.patcher.stop()

    def test_search_tracks_basic(self):
        """Test searching tracks with basic fields"""
        fields = "tracks.items.id,tracks.items.name,tracks.items.artists.name,tracks.items.duration_ms"
        result = SpotifyService.search_spotify(
            q="test query", search_type="track", fields=fields
        )

        expected = {
            "tracks": {
                "items": [
                    {
                        "id": "track_id",
                        "name": "Track Name",
                        "artists": [{"name": "Artist Name"}],
                        "duration_ms": 180000,
                    }
                ]
            }
        }
        assert result == expected

    def test_search_artists_basic(self):
        """Test searching artists with basic fields"""
        fields = "artists.items.id,artists.items.name,artists.items.genres,artists.items.popularity"
        result = SpotifyService.search_spotify(
            q="test query", search_type="artist", fields=fields
        )

        expected = {
            "artists": {
                "items": [
                    {
                        "id": "artist_id",
                        "name": "Artist Name",
                        "genres": ["Prog rock", "Grunge"],
                        "popularity": 80,
                    }
                ]
            }
        }
        assert result == expected

    def test_search_albums_with_artists(self):
        """Test searching albums with artist information"""
        fields = "albums.items.id,albums.items.name,albums.items.artists.name,albums.items.release_date,albums.items.total_tracks"
        result = SpotifyService.search_spotify(
            q="test query", search_type="album", fields=fields
        )

        expected = {
            "albums": {
                "items": [
                    {
                        "id": "album_id",
                        "name": "Album Name",
                        "artists": [{"name": "Artist Name"}],
                        "release_date": "1981-12",
                        "total_tracks": 12,
                    }
                ]
            }
        }
        assert result == expected

    def test_search_tracks_full_details(self):
        """Test searching tracks with full details"""
        fields = (
            "tracks.items.id,tracks.items.name,tracks.items.artists.name,"
            "tracks.items.album.name,tracks.items.album.release_date,"
            "tracks.items.duration_ms,tracks.items.popularity,tracks.items.preview_url"
        )
        result = SpotifyService.search_spotify(
            q="test query", search_type="track", fields=fields
        )

        expected = {
            "tracks": {
                "items": [
                    {
                        "id": "track_id",
                        "name": "Track Name",
                        "artists": [{"name": "Artist Name"}],
                        "album": {
                            "name": "Album Name",
                            "release_date": "1981-12",
                        },
                        "duration_ms": 180000,
                        "popularity": 75,
                        "preview_url": "https://preview.url",
                    }
                ]
            }
        }
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
