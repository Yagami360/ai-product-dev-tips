# Conceptual Example: Defining Hierarchy
from google.adk.agents import LlmAgent

# Define individual ai agents
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

# Create parent agent and assign children via sub_agents
multi_agent = LlmAgent(
    name="MultiAgentWithHierarchy",
    model="gemini-2.0-flash",
    description="I coordinate greetings and jokes.",
    # Assign sub_agents here
    sub_agents=[
        greeter_agent,
        joke_agent
    ]
)
# parent agent を root agent として設定
root_agent = multi_agent

# Framework automatically sets:
# assert greeter.parent_agent == coordinator
# assert task_doer.parent_agent == coordinator
