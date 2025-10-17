import asyncio
import httpx
from a2a.client import A2ACardResolver
from agent_framework.a2a import A2AAgent


A2A_AGENT_HOST_URL = "http://localhost:8080"

async def create_a2a_agent():
    # case1: Create A2A agent with card resolver
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        resolver = A2ACardResolver(httpx_client=http_client, base_url=A2A_AGENT_HOST_URL)
        agent_card = await resolver.get_agent_card(relative_card_path="/.well-known/agent.json")
        agent = A2AAgent(
            name=agent_card.name,
            description=agent_card.description,
            agent_card=agent_card,
            url=A2A_AGENT_HOST_URL,
        )

    # case2: Create A2A agent with direct URL configuration
    # agent = A2AAgent(
    #     name="My A2A Agent",
    #     description="A directly configured A2A agent",
    #     url=f"{A2A_AGENT_HOST_URL}/echo",
    # )

    return agent


async def main():
    agent = await create_a2a_agent()
    result = await agent.run("Tell me a joke about a pirate.")
    print(result.text)

asyncio.run(main())
