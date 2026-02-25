from util.state import PostState
from langchain.tools import tool


@tool
def getInfoFromAnalyticsAI(prompt : PostState):
    """
    ask AnaylisisAI for this ngo a appropriate question based on
    in decide and optimize the prompt and caption. 
    """
    return