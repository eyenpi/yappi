import inspect
from llama_index.core.tools import FunctionTool
from api.services.spotify_service import SpotifyService
from typing import List


def create_spotify_tools() -> List[FunctionTool]:
    """Create Spotify-specific LlamaIndex tools automatically from SpotifyService methods."""
    tools = []

    for name, method in inspect.getmembers(
        SpotifyService, predicate=inspect.isfunction
    ):
        if not name.startswith("_"):  # Skip private methods
            tool = FunctionTool.from_defaults(
                fn=method,
                name=name,
                description=getattr(method, "yaml_doc", f"Call {name} on Spotify API"),
            )
            tools.append(tool)

    return tools


# Create tools once at module level
spotify_tools = create_spotify_tools()
