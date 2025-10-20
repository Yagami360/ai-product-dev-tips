# ---------------------------------
# Step 1: Define tools and model
# ---------------------------------
from langchain.tools import tool
from langchain.chat_models import init_chat_model


model = init_chat_model(
    "google_genai:gemini-2.5-flash",
    temperature=0,
    
)

# ---------------------------------
# Step 2: Define state
# ---------------------------------
from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int

# ---------------------------------
# Step 3: Define AI Agents
# ---------------------------------
from langchain.messages import SystemMessage


def greeter_agent(state: dict):
    return {
        "messages": [
            model.invoke(
                [
                    SystemMessage(
                        content="You are a greeter in a friendly manner in Japanese."
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }


def joke_agent(state: dict):
    return {
        "messages": [
            model.invoke(
                [
                    SystemMessage(
                        content="You are a joke generator in Japanese."
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }

# ---------------------------------
# Step 4: Build Graph (workflow)
# ---------------------------------
from langgraph.graph import StateGraph, START, END

# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("greeter_agent", greeter_agent)
agent_builder.add_node("joke_agent", joke_agent)

# Add edges to connect nodes
agent_builder.add_edge(START, "greeter_agent")
agent_builder.add_edge("joke_agent", "greeter_agent")
agent_builder.add_edge("joke_agent", END)

# Compile the graph
agent = agent_builder.compile()

# Show the graph
from IPython.display import Image, display
display(Image(agent.get_graph(xray=True).draw_mermaid_png()))

# ---------------------------------
# Step 5: Run Graph (workflow)
# ---------------------------------
# Run graph
from langchain.messages import HumanMessage
messages = [
    HumanMessage(content="何ができますか？"),
    HumanMessage(content="あいさつして"),
    HumanMessage(content="ジョークを言って")
]
messages = agent.invoke({"messages": messages})
for m in messages["messages"]:
    m.pretty_print()
