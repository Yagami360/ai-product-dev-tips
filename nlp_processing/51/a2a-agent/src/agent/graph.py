"""LangGraph A2A conversational agent.

Supports the A2A protocol with messages input for conversational interactions.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


class Context(TypedDict):
    """Context parameters for the agent."""
    my_configurable_param: str


@dataclass
class State:
    """Input state for the agent.

    Defines the initial structure for A2A conversational messages.
    """
    messages: List[Dict[str, Any]]


async def call_model(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Process conversational messages and returns output using Gemini."""
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {
            "messages": state.messages + [{
                "role": "assistant",
                "content": "Error: GOOGLE_API_KEY environment variable is not set."
            }]
        }

    # Initialize Gemini model using LangChain
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.7,
        max_output_tokens=100,
    )

    # Process the incoming messages
    latest_message = state.messages[-1] if state.messages else ""

    # Handle different message formats (dict or string)
    if isinstance(latest_message, dict):
        user_content = latest_message.get("content", "No message content")
    elif isinstance(latest_message, str):
        user_content = latest_message
    else:
        user_content = str(latest_message) if latest_message else "No message content"

    # Prepare messages for the model using LangChain message objects
    messages = [
        SystemMessage(content="You are a helpful conversational agent. Keep responses brief and engaging."),
        HumanMessage(content=user_content)
    ]

    try:
        # Make API call using LangChain in a thread-safe manner
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: model.invoke(messages)
        )
        ai_response = response.content

    except Exception as e:
        ai_response = f"I received your message but had trouble processing it. Error: {str(e)[:50]}..."

    # Create a response message
    response_message = {
        "role": "assistant",
        "content": ai_response
    }

    return {
        "messages": state.messages + [response_message]
    }


# Define the graph
graph = (
    StateGraph(State, context_schema=Context)
    .add_node(call_model)
    .add_edge("__start__", "call_model")
    .compile()
)
