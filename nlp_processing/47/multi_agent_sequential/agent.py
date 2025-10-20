# Conceptual Example: Sequential Pipeline
from google.adk.agents import SequentialAgent, LlmAgent

# 個々の AI Agent を定義
greeter_agent = LlmAgent(
    # あいさつする AI Agent
    name="Greeter",
    model="gemini-2.0-flash",
    description="I greet the user.",
    instruction="Greet the user in a friendly manner in Japanese.",
)
joke_agent = LlmAgent(
    # 冗談を生成する AI Agent
    name="JokeGenerator",
    model="gemini-2.0-flash",
    description="I generate jokes.",
    instruction="Generate a joke for the user in Japanese.",
)

# 直列処理でのマルチ AI Agent を定義
multi_agent = SequentialAgent(
    name="MultiAgentWithSequential",
    sub_agents=[greeter_agent, joke_agent]
)
root_agent = multi_agent
