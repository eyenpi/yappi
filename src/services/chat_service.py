from src.agents.spotify_agent import spotify_agent
from src.agents.user_experience_agent import ux_agent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    @staticmethod
    async def handle_spotify_chat(task: str):
        """
        Handles a chat request using the Spotify agent.
        """
        termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(
            max_messages=5
        )
        team = SelectorGroupChat(
            [spotify_agent, ux_agent],
            model_client=OpenAIChatCompletionClient(model="gpt-4o", temperature=0.5),
            termination_condition=termination,
        )
        try:
            response = await team.run(task=task)
            logger.info(f"Chat response: {response}")
            if response:
                return response.messages[-1].content.replace("TERMINATE", "").strip()
        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
