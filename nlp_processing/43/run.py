import asyncio
from typing import Any
from azure.identity.aio import AzureCliCredential
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework import ConcurrentBuilder
from agent_framework import ChatMessage, Role, WorkflowOutputEvent, WorkflowViz


def create_workflow(chat_client: AzureOpenAIChatClient) -> None:
    # カスタムアグリゲーター関数を定義（chat_clientにアクセスするためにクロージャーを使用）
    async def summarize_results(results: list[Any], ctx: Any) -> str:
        # Extract one final assistant message per agent
        expert_sections: list[str] = []
        for r in results:
            try:
                messages = getattr(r.agent_run_response, "messages", [])
                final_text = messages[-1].text if messages and hasattr(messages[-1], "text") else "(no content)"
                expert_sections.append(f"{getattr(r, 'executor_id', 'expert')}:\n{final_text}")
            except Exception as e:
                expert_sections.append(f"{getattr(r, 'executor_id', 'expert')}: (error: {type(e).__name__}: {e})")

        # Ask the model to synthesize a concise summary of the experts' outputs
        system_msg = ChatMessage(
            Role.SYSTEM,
            text=(
                "あなたは複数のドメイン専門家の出力を1つのまとまりのある簡潔な要約に統合する"
                "優秀なアシスタントです。重要なポイントを明確にして、200語以内にまとめてください。"
            ),
        )
        user_msg = ChatMessage(Role.USER, text="\n\n".join(expert_sections))

        response = await chat_client.get_response([system_msg, user_msg])
        # Return the model's final assistant text as the completion result
        return response.messages[-1].text if response.messages else ""
    
    # 1) AI Agent を作成する
    researcher = chat_client.create_agent(
        instructions=(
            "あなたは市場調査と製品調査の専門家です。与えられたプロンプトに対して、簡潔で事実に基づいた洞察、機会、リスクを提供してください。"
        ),
        name="researcher",
    )

    marketer = chat_client.create_agent(
        instructions=(
            "あなたは創造的なマーケティング戦略家です。プロンプトに沿った魅力的な価値提案とターゲットメッセージを作成してください。"
        ),
        name="marketer",
    )

    legal = chat_client.create_agent(
        instructions=(
            "あなたは慎重な法務・コンプライアンスレビュアーです。プロンプトに基づいて制約、免責事項、ポリシー上の懸念事項を強調してください。"
        ),
        name="legal",
    )

    # 2) マルチ AI Agent から構成される並列処理のワークフローを作成する
    # デフォルトの aggregator を使用する場合
    # workflow = (
    #     ConcurrentBuilder()
    #     .participants([researcher, marketer, legal])
    #     .build()
    # )
    # 独自の aggregator を使用する場合
    workflow = (
        ConcurrentBuilder()
        .participants([researcher, marketer, legal])
        .with_aggregator(summarize_results)
        .build()
    )
    return workflow


# 3) ワークフローを実行する
# Run with a single prompt, stream progress, and pretty-print the final combined messages
async def run_workflow(workflow) -> None:
    completion: WorkflowOutputEvent | None = None
    input_prompt = "新しい価格帯の電動自転車を都市部での通勤に向けて発売することについて、市場調査と製品調査を行ってください。"
    print("入力プロンプト: ", input_prompt)
    async for event in workflow.run_stream(input_prompt):
        if isinstance(event, WorkflowOutputEvent):
            completion = event

    if completion:
        print("===== 最終的な応答 (messages) =====")
        # デフォルトの aggregator を使用する場合
        # messages: list[ChatMessage] | Any = completion.data
        # for i, msg in enumerate(messages, start=1):
        #     name = msg.author_name if msg.author_name else "user"
        #     print(f"{'-' * 60}\n\n{i:02d} [{name}]:\n{msg.text}")

        # 独自の aggregator を使用する場合
        print(completion.data)


if __name__ == "__main__":
    chat_client = AzureOpenAIChatClient(credential=AzureCliCredential())

    # AI Agent とワークフローを作成
    workflow = create_workflow(chat_client)

    # ワークフローを実行
    asyncio.run(run_workflow(workflow))

    # ワークフローの視覚化を行う
    viz = WorkflowViz(workflow)
    viz.save_png("workflow_vis.png")
    print("Mermaid flowchart:\n", viz.to_mermaid())
