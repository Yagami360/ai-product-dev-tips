#!/usr/bin/env python3
"""Agent-to-Agent conversation simulation using LangGraph A2A protocol."""

import asyncio
import aiohttp
import os

async def send_message(session, port, assistant_id, text):
    """Send a message to an agent and return the response text."""
    url = f"http://127.0.0.1:{port}/a2a/{assistant_id}"
    payload = {
        "jsonrpc": "2.0",
        "id": "",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}]
            },
            "messageId": "",
            "thread": {"threadId": ""}
        }
    }

    headers = {"Accept": "application/json"}
    async with session.post(url, json=payload, headers=headers) as response:
        try:
            result = await response.json()
            return result["result"]["artifacts"][0]["parts"][0]["text"]
        except Exception as e:
            text = await response.text()
            print(f"Response error from port {port}: {response.status} - {text}")
            return f"Error from port {port}: {response.status}"

async def simulate_conversation():
    """Simulate a conversation between two agents."""
    agent_a_id = os.getenv("AGENT_A_ID")
    agent_b_id = os.getenv("AGENT_B_ID")

    if not agent_a_id or not agent_b_id:
        print("Set AGENT_A_ID and AGENT_B_ID environment variables")
        return

    message = "Hello! Let's have a conversation."

    async with aiohttp.ClientSession() as session:
        for i in range(3):
            print(f"--- Round {i + 1} ---")

            # Agent A responds
            message = await send_message(session, 2024, agent_a_id, message)
            print(f"🔵 Agent A: {message}")

            # Agent B responds
            message = await send_message(session, 2025, agent_b_id, message)
            print(f"🔴 Agent B: {message}")
            print()

if __name__ == "__main__":
    asyncio.run(simulate_conversation())
