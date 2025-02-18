from llama_index.agent.openai import OpenAIAssistantAgent
from typing import Dict
from api.core.langfuse_integration import instrumentor
from api.core.assistant_factory import assistant_factory


class AgentManager:
    def __init__(self):
        self._thread_ids: Dict[str, str] = {}  # session_id -> thread_id

    def _get_agent_for_session(
        self, session_id: str, api_id: str
    ) -> OpenAIAssistantAgent:
        """Get agent with the session's thread ID or create new one if first time"""
        # Get the tools for this API
        tools = assistant_factory._api_tools[api_id]

        if session_id not in self._thread_ids:
            # First time - create a new thread
            agent = OpenAIAssistantAgent.from_existing(
                assistant_id=assistant_factory.assistants[api_id],
                tools=tools,
                verbose=True,
            )
            print(agent.assistant.id)
            self._thread_ids[session_id] = agent.thread_id
            return agent

        # Reuse existing thread with the requested assistant
        return OpenAIAssistantAgent.from_existing(
            assistant_id=assistant_factory.assistants[api_id],
            thread_id=self._thread_ids[session_id],
            tools=tools,
            verbose=True,
        )

    def cleanup_session(self, session_id: str) -> None:
        """Clean up thread for a specific session"""
        if session_id in self._thread_ids:
            del self._thread_ids[session_id]

    async def process_message(
        self, api_id: str, message: str, session_id: str, user_id: str
    ) -> str:
        """Process a message using the specified agent"""
        if api_id not in assistant_factory.assistants:
            raise ValueError(f"No assistant found for API {api_id}")

        agent = self._get_agent_for_session(session_id, api_id)

        with instrumentor.observe(
            user_id=user_id,
            session_id=session_id,
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
