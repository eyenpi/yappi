from llama_index.agent.openai import OpenAIAssistantAgent
from typing import Dict, Optional, List
import yaml
from pathlib import Path
from api.tools.spotify_tools import spotify_tools
from api.tools.ticketmaster_tools import ticketmaster_tools

from api.core.langfuse_integration import instrumentor


class AgentManager:
    def __init__(self):
        self._base_agents: Dict[str, OpenAIAssistantAgent] = {}
        self._session_agents: Dict[str, Dict[str, OpenAIAssistantAgent]] = (
            {}
        )  # session_id -> {api_id -> agent}
        self._api_tools: Dict[str, List] = {
            "spotify": spotify_tools,
            "ticketmaster": ticketmaster_tools,
        }
        self._load_instructions()
        self._initialize_predefined_agents()

    def _load_instructions(self) -> None:
        """Load assistant instructions from YAML file"""
        docs_path = (
            Path(__file__).parent.parent / "docs" / "assistant_instructions.yaml"
        )
        with open(docs_path) as f:
            self._api_instructions = yaml.safe_load(f)

    def _create_agent(
        self,
        api_id: str,
        assistant_id: Optional[str] = None,
    ) -> OpenAIAssistantAgent:
        """Create a new agent instance"""
        tools = self._api_tools[api_id]
        instructions = self._api_instructions.get(api_id, {}).get(
            "instructions", self._api_instructions["default"]["instructions"]
        )
        instructions = instructions.format(api_name=api_id.title())

        if assistant_id:
            # Use existing assistant but create new thread
            return OpenAIAssistantAgent.from_existing(
                assistant_id=assistant_id,
                verbose=True,
            )
        else:
            # Create completely new assistant
            return OpenAIAssistantAgent.from_new(
                name=f"{api_id.title()} Assistant",
                instructions=instructions,
                tools=tools,
                model="gpt-4o",
                verbose=True,
            )

    def _initialize_predefined_agents(self) -> None:
        """Initialize predefined agents"""
        for api_id in self._api_tools:
            self._base_agents[api_id] = self._create_agent(api_id)

    def _get_or_create_session_agent(
        self, session_id: str, api_id: str
    ) -> OpenAIAssistantAgent:
        """Get existing agent or create new one for session/api combination"""
        if session_id not in self._session_agents:
            self._session_agents[session_id] = {}

        if api_id not in self._session_agents[session_id]:
            # Create new agent using the base agent's assistant ID
            base_agent = self._base_agents[api_id]
            new_agent = self._create_agent(
                api_id,
                assistant_id=base_agent.assistant.id,
            )
            self._session_agents[session_id][api_id] = new_agent

        return self._session_agents[session_id][api_id]

    def cleanup_session(self, session_id: str) -> None:
        """Clean up agents for a specific session"""
        if session_id in self._session_agents:
            del self._session_agents[session_id]

    async def process_message(
        self, api_id: str, message: str, session_id: str, user_id: str
    ) -> str:
        """Process a message using the specified agent"""
        if api_id not in self._base_agents:
            raise ValueError(f"No agent found for API {api_id}")

        agent = self._get_or_create_session_agent(session_id, api_id)

        with instrumentor.observe(
            user_id=user_id,
            session_id=agent.thread_id,
        ) as trace:
            try:
                response = await agent.achat(message)
                if isinstance(response, dict) and "content" in response:
                    return str(response["content"])
                return str(response)
            except Exception as e:
                print(f"Error processing message: {e}")
                return "Sorry, there was an error processing your message."


agent_manager = AgentManager()
