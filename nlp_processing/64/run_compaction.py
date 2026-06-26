import argparse

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.messages.utils import count_tokens_approximately
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver

# 長期化する会話を模した複数ターンのユーザー発話。
# 後半ほど履歴が積み上がり、SummarizationMiddleware の閾値（trigger）を超えると
# 古いメッセージが要約（compaction）されて履歴が圧縮される。
TURNS = [
    "私の名前は坂井です。今日から旅行の計画を一緒に立ててください。行き先は京都です。",
    "京都では2泊3日を予定しています。寺社巡りと和食が好きです。予算は1人5万円くらい。",
    "1日目は伏見稲荷大社と清水寺に行きたいです。移動は公共交通機関を使います。",
    "2日目は嵐山に行きたい。竹林と渡月橋、それと湯豆腐のお店も知りたいです。",
    "3日目は午前中だけ空いています。京都駅周辺で買えるおすすめのお土産を教えて。",
    "ところで、私の名前は何でしたか？そして旅行の行き先と予算を覚えていますか？",
]


def build_agent(chat_model, summary_model, trigger_tokens, keep_messages):
    # SummarizationMiddleware が compaction 本体。
    # trigger=("tokens", N): 履歴が約 N トークンを超えたら要約を発火。
    # keep=("messages", M): 要約後に直近 M メッセージだけを残し、それ以前を要約に置き換える。
    return create_agent(
        model=chat_model,
        tools=[],  # ツール無しの純粋な会話エージェント（CPU で軽く回すため）
        middleware=[
            SummarizationMiddleware(
                model=summary_model,
                trigger=("tokens", trigger_tokens),
                keep=("messages", keep_messages),
            ),
        ],
        checkpointer=InMemorySaver(),  # thread_id 単位で会話履歴を保持し、ターンをまたいで蓄積させる
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen3.5:4b", help="会話＆要約に使う Ollama モデル")
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--trigger-tokens", type=int, default=400, help="この概算トークン数を超えたら compaction を発火")
    parser.add_argument("--keep-messages", type=int, default=4, help="要約後に残す直近メッセージ数")
    args = parser.parse_args()

    # reasoning=False で Qwen3.5 の思考（thinking）生成を無効化し、CPU での応答を軽くする。
    llm = ChatOllama(model=args.model, base_url=args.base_url, temperature=0, reasoning=False)
    agent = build_agent(llm, llm, args.trigger_tokens, args.keep_messages)
    config = {"configurable": {"thread_id": "demo"}}

    print(f"=== 閾値要約 compaction（LangChain SummarizationMiddleware）  model = {args.model} ===")
    print(f"trigger = (tokens, {args.trigger_tokens}),  keep = (messages, {args.keep_messages})\n")

    prev_n = 0
    for i, user_msg in enumerate(TURNS, 1):
        agent.invoke({"messages": [{"role": "user", "content": user_msg}]}, config)
        msgs = agent.get_state(config).values["messages"]
        n_msgs = len(msgs)
        approx_tokens = count_tokens_approximately(msgs)

        # compaction が起きると、2 メッセージ（user + AI）を足したのに総数がむしろ減る。
        compacted = n_msgs < prev_n + 2
        prev_n = n_msgs

        answer = msgs[-1].content if isinstance(msgs[-1].content, str) else str(msgs[-1].content)
        print(f"[turn {i}] U: {user_msg}")
        print(f"         A: {answer.strip()[:80]}")
        print(f"         履歴: {n_msgs} メッセージ / 概算 {approx_tokens} tokens" + ("  ← compaction 発火" if compacted else ""))
        print()

    print("=" * 60)
    print("→ 最終ターンで名前・行き先・予算を答えられていれば、compaction 後も")
    print("  重要情報が要約として保持できている（圧縮しても文脈が途切れていない）。")


if __name__ == "__main__":
    main()
