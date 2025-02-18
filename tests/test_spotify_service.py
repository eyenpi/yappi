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
                    "artists": {"name": "string"},
                    "images": {
                        "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228"
                    },
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
                    "artists": {"name": "string"},
                    "images": {
                        "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228"
                    },
                    "external_urls": {"spotify": "string"},
                }
            ],
        }
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
