from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from api.services.spotify_service import SpotifyService
from autogen_core.tools import FunctionTool

search_spotify_tool = FunctionTool(
    SpotifyService.search_spotify, description="Search Spotify content."
)

spotify_agent = AssistantAgent(
    name="spotify_expert",
    model_client=OpenAIChatCompletionClient(model="gpt-4o", temperature=0.0),
    tools=[search_spotify_tool],
    system_message="You are a Spotify expert who can interact with the Spotify API.",
)
