from langgraph.graph import StateGraph, START, END
from util.state import PostState
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from util.tools import tools
from langgraph.checkpoint.memory import MemorySaver
from agent.chatbot import chatbot


graph_builder = StateGraph(PostState)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)