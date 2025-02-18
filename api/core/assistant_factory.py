from llama_index.agent.openai import OpenAIAssistantAgent
from typing import Dict
import yaml
from pathlib import Path
from api.tools.spotify_tools import spotify_tools
from api.tools.ticketmaster_tools import ticketmaster_tools


class AssistantFactory:
    def __init__(self):
        self._api_tools = {
            "spotify": spotify_tools,
            "ticketmaster": ticketmaster_tools,
        }
        self._load_instructions()
        self.assistants: Dict[str, str] = {}  # api_id -> assistant_id
        self._initialize_assistants()

    def _load_instructions(self) -> None:
        """Load assistant instructions from YAML file"""
        docs_path = (
            Path(__file__).parent.parent / "docs" / "assistant_instructions.yaml"
        )
        with open(docs_path) as f:
            self._api_instructions = yaml.safe_load(f)

    def _create_assistant(self, api_id: str) -> str:
        """Create a new assistant and return its ID"""
        tools = self._api_tools[api_id]
        instructions = self._api_instructions.get(api_id, {}).get(
            "instructions", self._api_instructions["default"]["instructions"]
        )
        instructions = instructions.format(api_name=api_id.title())
        agent = OpenAIAssistantAgent.from_new(
            name=f"{api_id.title()} Assistant",
            instructions=instructions,
            tools=tools,
            model="gpt-4o",
            verbose=True,
        )
        return agent.assistant.id

    def _initialize_assistants(self) -> None:
        """Initialize all assistants at startup"""
        for api_id in self._api_tools:
            self.assistants[api_id] = self._create_assistant(api_id)


assistant_factory = AssistantFactory()
