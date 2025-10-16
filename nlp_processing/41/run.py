import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

agent = AzureOpenAIChatClient(credential=AzureCliCredential()).create_agent(
    instructions="あなたはジョークを言うことができるエージェントです。",
    name="JokeAgent"
)

async def main():
    result = await agent.run("ジョークを言ってください")
    print(result.text)

asyncio.run(main())