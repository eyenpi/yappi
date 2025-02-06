from llama_index.agent.openai import OpenAIAssistantAgent
from typing import Dict, Optional, List
import yaml
from pathlib import Path
from api.tools.spotify_tools import spotify_tools

# Import other tool sets as needed
# from api.tools.other_tools import other_tools
from api.core.langfuse_integration import instrumentor
from api.models.thread_models import UserThread
from api.db.supabase_client import supabase


class AgentManager:
    def __init__(self):
        self._base_agents: Dict[str, OpenAIAssistantAgent] = {}
        self._user_agents: Dict[str, Dict[str, OpenAIAssistantAgent]] = {}
        self._api_tools: Dict[str, List] = {
            "spotify": spotify_tools,
            # Add other API tools mappings here
            # "other_api": other_tools,
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
        thread_id: Optional[str] = None,
    ) -> OpenAIAssistantAgent:
        """Centralized agent creation method"""
        tools = self._api_tools[api_id]
        instructions = self._api_instructions.get(api_id, {}).get(
            "instructions", self._api_instructions["default"]["instructions"]
        )
        instructions = instructions.format(api_name=api_id.title())

        if thread_id and assistant_id:
            return OpenAIAssistantAgent.from_existing(
                assistant_id=assistant_id,
                tools=tools,
                thread_id=thread_id,
                verbose=True,
            )
        else:
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

    def _get_authenticated_client(self, access_token: str):
        """Create a new authenticated Supabase client"""
        client = supabase
        # Set auth header directly instead of using set_session
        client.postgrest.auth(access_token)
        return client

    async def _load_user_thread(
        self, user_id: str, api_id: str, access_token: str
    ) -> Optional[UserThread]:
        """Load user thread from database"""
        client = self._get_authenticated_client(access_token)
        result = (
            client.table("user_threads")
            .select("*")
            .eq("user_id", user_id)
            .eq("api_id", api_id)
            .execute()
        )
        if result.data:
            return UserThread(**result.data[0])
        return None

    async def _save_user_thread(self, thread: UserThread, access_token: str) -> None:
        """Save user thread to database"""
        client = self._get_authenticated_client(access_token)
        thread_dict = thread.dict()
        # Convert UUID and datetime to strings for Supabase
        thread_dict["id"] = str(thread_dict["id"])
        thread_dict["created_at"] = thread_dict["created_at"].isoformat()
        client.table("user_threads").upsert(thread_dict).execute()

    async def _get_or_create_agent(
        self, user_id: str, api_id: str, access_token: str
    ) -> OpenAIAssistantAgent:
        """Get existing agent or create new one for user/api combination"""
        if user_id not in self._user_agents:
            self._user_agents[user_id] = {}

        if api_id not in self._user_agents[user_id]:
            # Try to load existing thread from database
            thread_data = await self._load_user_thread(user_id, api_id, access_token)
            base_agent = self._base_agents[api_id]

            if thread_data:
                new_agent = self._create_agent(
                    api_id,
                    assistant_id=thread_data.assistant_id,
                    thread_id=thread_data.thread_id,
                )
            else:
                new_agent = self._create_agent(
                    api_id,
                    assistant_id=base_agent.assistant.id,
                )
                print("Creating new user thread")
                thread_data = UserThread(
                    user_id=user_id,
                    api_id=api_id,
                    assistant_id=base_agent.assistant.id,
                    thread_id=new_agent.thread_id,
                )
                await self._save_user_thread(thread_data, access_token)

            self._user_agents[user_id][api_id] = new_agent

        return self._user_agents[user_id][api_id]

    async def process_message(self, api_id: str, message: str, user_data) -> str:
        """Process a message using the specified agent"""
        if api_id not in self._base_agents:
            raise ValueError(f"No agent found for API {api_id}")

        user_id = user_data["id"]
        access_token = user_data["access_token"]
        agent = await self._get_or_create_agent(user_id, api_id, access_token)

        with instrumentor.observe(
            user_id=user_id,
            session_id=agent.thread_id,
        ) as trace:
            # # Add user message to thread
            # agent.add_message(message)

            # # Run the assistant and let it make multiple function calls
            # run, messages = await agent.arun_assistant()

            # # Get the final response after all function calls
            # response = str(agent.latest_message.content)
            response = await agent.achat(message)

        # instrumentor.flush()
        return str(response)


agent_manager = AgentManager()
