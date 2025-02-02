from llama_index.agent.openai import OpenAIAgent
from typing import Dict
from api.tools.spotify_tools import create_spotify_tools
from api.core.langfuse_integration import instrumentor


class AgentManager:
    def __init__(self):
        self._agents: Dict[str, OpenAIAgent] = {}
        self._initialize_predefined_agents()

    def _initialize_predefined_agents(self) -> None:
        """Initialize predefined agents"""
        spotify_agent = OpenAIAgent.from_tools(
            create_spotify_tools(),
            verbose=True,
            system_prompt="You are a Spotify assistant. Help users find music using Spotify's API.",
        )
        self._agents["spotify"] = spotify_agent

    async def process_message(self, api_id: str, message: str) -> str:
        """Process a message using the specified agent"""
        agent = self._agents.get(api_id)
        if not agent:
            raise ValueError(f"No agent found for API {api_id}")

        response = str(agent.chat(message))
        instrumentor.flush()  # Flush events after each chat
        return response


agent_manager = AgentManager()
