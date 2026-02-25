from langchain_tavily import TavilySearch
import os

websearch = TavilySearch(
    tavily_api_key=os.getenv("TAVILY_API_KEY"),
    max_results=5,
    topic="general",
)
