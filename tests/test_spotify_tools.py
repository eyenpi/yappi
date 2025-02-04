import pytest
from api.tools.spotify_tools import spotify_tools
from api.services.spotify_service import SPOTIFY_DOCS


def test_spotify_tools_creation():
    """Test if Spotify tools are created correctly"""
    # Check if tools were created
    assert len(spotify_tools) > 0, "No tools were created"

    # Find the search tool
    print()
    for tool in spotify_tools:
        print(tool.metadata.description)


if __name__ == "__main__":
    pytest.main([__file__])
