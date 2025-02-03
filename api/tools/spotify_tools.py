from llama_index.core.tools import FunctionTool
from api.services.spotify_service import SpotifyService
from typing import List


def create_spotify_tools() -> List[FunctionTool]:
    """Create Spotify-specific LlamaIndex tools"""

    search_tool = FunctionTool.from_defaults(
        fn=SpotifyService.search_spotify,
        name="search_spotify",
        description="Search for music on Spotify",
    )

    return [search_tool]


# Create tools once at module level
spotify_tools = create_spotify_tools()
