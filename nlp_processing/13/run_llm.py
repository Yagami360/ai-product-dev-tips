import json
import argparse

from langchain.llms import OpenAI
from langchain.agents import Tool
from langchain.agents import initialize_agent
from langchain.agents import AgentType
# from langchain_community.utilities import SerpAPIWrapper


def get_weather(location):
    if location in ["東京", "Tokyo"]:
        weather = "曇り"
    elif location in ["広島", "Hiroshima"]:
        weather = "晴れ"
    else:
        weather = "不明"

    resp = [
        {"天気": weather}
    ]

    # Function calling での外部関数は、json データで戻り値を返す必要あり
    return json.dumps(resp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', type=str, default="gpt-3.5-turbo-0613")     # OpenAI Functions Agent 対応のモデルを指定する必要あり
    parser.add_argument('--prompt', type=str, default="広島の天気を教えて")
    args = parser.parse_args()

    # ---------------------------------
    # モデル定義
    # ---------------------------------
    llm = OpenAI(
        model_name=args.model_name,
        temperature=0.0,
    )
    print("llm: ", llm)

    # ---------------------------------
    # LangChain Agents の Tools 定義
    # Tools : Agent が外部とやり取りをするために呼び出す外部関数や外部ツール
    # ---------------------------------
    tools = [
        Tool(
            name = "GetWeather",
            func=get_weather,
            description="天気を知りたい場所を入力。例: 東京"
        ),
        # Tool(
        #     name="GoogleSearch",
        #     func=SerpAPIWrapper().run,
        #     description="useful for when you need to answer questions about current events. You should ask targeted questions"
        # ),
    ]
    print("tools: ", tools)

    # ---------------------------------
    # Agent オブジェクト作成
    # ---------------------------------
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,    # AgentType.OPENAI_FUNCTIONS : OpenAI Functions Agent
        verbose=True,
    )

    # ---------------------------------
    # Agent 実行（LLM 推論で最適な外部ツール実行）
    # ---------------------------------
    try:
        resp = agent.run(input=args.prompt)
        print(f"resp: {resp}")
    except Exception as e:
        print(f"Excception was occurred | {e}")
        exit(1)

    exit(0)
