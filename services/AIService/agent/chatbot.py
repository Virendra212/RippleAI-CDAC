from typing import Dict

from langchain_groq import ChatGroq
from util.tools import tools
from util.state import PostState
from langchain_core.messages import HumanMessage, ToolMessage
import logging
import time
import os
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI


google_api_key = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# ------------ Logging ------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm_google = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=google_api_key,
    temperature=0.7,
)


llm_groq = ChatGroq(
    model="llama-3.1-8b-instant",  
    api_key=groq_api_key,
    temperature=0.7,
)


#llm_with_tools = llm_groq.bind_tools(tools=tools)
llm_with_tools = llm_groq.bind_tools(tools=tools)


def chatbot(state: PostState) -> Dict:
    logger.info("Chatbot node running...")

    try:
        messages = state["messages"]

        # throttle for Groq
        time.sleep(1.2)

        response = llm_with_tools.invoke(messages)

        # If model wants to call a tool, let LangGraph handle it
        if isinstance(response, AIMessage) and response.tool_calls:
            return {"messages": messages + [response]}

        return {"messages": messages + [response]}

    except Exception as e:
        logger.error(f"Error in chatbot: {e}")
        return {
            "messages": messages + [HumanMessage(content="Internal error occurred")]
        }

