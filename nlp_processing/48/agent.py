from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
# AGENT_CARD_WELL_KNOWN_PATH=".well-known/agent-card.json"
print("AGENT_CARD_WELL_KNOWN_PATH:", AGENT_CARD_WELL_KNOWN_PATH)

root_agent = RemoteA2aAgent(
    name="RemoteA2aAgent",
    description=(
        "A helpful assistant for user questions."
    ),
    agent_card=f"http://localhost:8001/{AGENT_CARD_WELL_KNOWN_PATH}",
)
