from util.state import PostState
from langchain.tools import tool


@tool
def generateCaption(prompt : PostState):
    """
    generate the best suited caption . caption should be funny or 
    engaging or emotional and localized . 
    through which people can relate to.
    """
    return