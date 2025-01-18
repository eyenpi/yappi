from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

ux_agent = AssistantAgent(
    name="user_experience",
    model_client=OpenAIChatCompletionClient(model="gpt-4o", temperature=0.2),
    system_message="""You are the user interface agent that should talk to other agents and give the user the best experience.
    After all tasks are complete, summarize the findings and end with "TERMINATE".
    """,
)