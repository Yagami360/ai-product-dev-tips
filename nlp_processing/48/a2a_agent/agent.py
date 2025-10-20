from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
# from a2a.types import AgentCard

# AI Agent 定義
root_agent = LlmAgent(
    # あいさつする AI Agent
    name="Greeter",
    model="gemini-2.0-flash",
    description="I greet the user.",
    instruction="Greet the user in a friendly manner in Japanese.",
)

# case1: デフォルトの AgentCard を利用する場合
# to_a2a() メソッドを呼び出すだけで、A2A 対応 AI Agent を作成することができる
# デフォルトの AgentCard が自動的に設定される
a2a_app = to_a2a(root_agent, port=8001)

# case2: 独自の AgentCard を SDK で定義して利用する場合
# 独自の AgentCard を利用することも可能
# agent_card = AgentCard(
#     "name": "greeter_agent",
#     description="I greet the user.",
#     url="http://localhost:8001",
#     version="1.0.0",
#     capabilities={},
#     skills=[],
#     defaultInputModes=["text/plain"],
#     defaultOutputModes=["text/plain"],
#     supportsAuthenticatedExtendedCard=False,
# )
# a2a_app = to_a2a(root_agent, port=8001, agent_card=agent_card)

# case3: JSON ファイルから AgentCard を読み込む場合
# JSON ファイルから AgentCard を読み込むことも可能
# a2a_app = to_a2a(root_agent, port=8001, agent_card=".well-known/agent-card.json")
