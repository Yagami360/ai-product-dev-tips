import asyncio
from collections.abc import Awaitable, Callable
from contextlib import AsyncExitStack
from typing import Any

from agent_framework import AgentRunUpdateEvent, WorkflowBuilder, WorkflowOutputEvent, WorkflowViz
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential


async def create_azure_ai_agent() -> tuple[Callable[..., Awaitable[Any]], Callable[[], Awaitable[None]]]:
    """Helper method to create a Azure AI agent factory and a close function.

    This makes sure the async context managers are properly handled.
    """
    stack = AsyncExitStack()
    cred = await stack.enter_async_context(AzureCliCredential())

    client = await stack.enter_async_context(AzureAIAgentClient(async_credential=cred))

    async def agent(**kwargs: Any) -> Any:
        return await stack.enter_async_context(client.create_agent(**kwargs))

    async def close() -> None:
        await stack.aclose()

    return agent, close


async def main() -> None:
    # Azure AI Agent Factory を作成する
    agent, close = await create_azure_ai_agent()

    try:
        # 複数 Agent を作成する
        writer = await agent(
            name="Writer",
            instructions=(
                "あなたは優秀なコンテンツライターです。"
                "新しいコンテンツを作成し、フィードバックに基づいてコンテンツを編集します。"
            ),
        )
        reviewer = await agent(
            name="Reviewer",
            instructions=(
                "あなたは優秀なコンテンツレビュワーです。"
                "提供されたコンテンツについて、ライターに実用的なフィードバックを提供してください。"
                "フィードバックは可能な限り簡潔に提供してください。"
            ),
        )

        # 複数 Agent でのワークフローを構築する
        # Add agents to workflow with custom settings using add_agent.
        # Agents adapt to workflow mode: run_stream() for incremental updates, run() for complete responses.
        # Reviewer agent emits final AgentRunResponse as a workflow output.
        workflow = (
            WorkflowBuilder()
            .add_agent(writer, id="Writer")
            .add_agent(reviewer, id="Reviewer", output_response=True)
            .set_start_executor(writer)
            .add_edge(writer, reviewer)
            .build()
        )

        last_executor_id: str | None = None

        input_prompt = "手頃な価格で運転が楽しい新しい電動SUVのキャッチコピーを作成してください。"
        print("input_prompt: ", input_prompt)
        events = workflow.run_stream(input_prompt)
        async for event in events:
            # print("vars(event): ", vars(event))
            if isinstance(event, AgentRunUpdateEvent):
                eid = event.executor_id
                if eid != last_executor_id:
                    if last_executor_id is not None:
                        print()
                    print(f"{eid}:", end=" ", flush=True)
                    last_executor_id = eid
                print(event.data, end="", flush=True)
            elif isinstance(event, WorkflowOutputEvent):
                print("\n===== Final output =====")
                print(event.data)

        # ワークフローの視覚化を行う
        viz = WorkflowViz(workflow)
        viz.save_png("workflow_vis.png")
        print("Mermaid flowchart:\n", viz.to_mermaid())

    finally:
        await close()


if __name__ == "__main__":
    asyncio.run(main())
