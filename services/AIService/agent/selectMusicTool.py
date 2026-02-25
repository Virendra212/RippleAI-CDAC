from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Annotated
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
import os

from util.state import PostState

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": False},
)

@tool
def selectMusic(
        state: PostState,
        tool_call_id: Annotated[str, InjectedToolCallId],
        query: str = ""          
    )-> Command:
    """Tool to retrieve song link from FAISS vector store based on input query."""
    try:

        folder_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "createVectors",
                "knowledgeBase",
                "songsStore"
            )
        folder_path = os.path.abspath(folder_path)


      
        # Load vector store
        vectors = FAISS.load_local(folder_path, embeddings, allow_dangerous_deserialization=True)
        retriever = vectors.as_retriever(search_kwargs={"k": 1})

        try:
            user_message = state.get("messages", [{}])[0].get("content", "")
        except Exception:
            user_message = ""

        # If state message empty, use query
        if not user_message:
            user_message = query

        if not user_message:
            return Command(update={
                "messages": [ToolMessage(
                    content="No user input found to retrieve information.",
                    name="retrieval_node",
                    tool_call_id=tool_call_id)]
            })

        # Run retrieval
        retrieved_docs = retriever.invoke(user_message)
        limited_content = "\n\n".join(doc.page_content[:300] for doc in retrieved_docs)

        return Command(update={
            "messages": [ToolMessage(
                content=limited_content or "No relevant information found.",
                name="retrieval_node",
                tool_call_id=tool_call_id)]
        })

    except Exception as e:
        return Command(update={
            "messages": [ToolMessage(
                content=f" Error: {str(e)}",
                name="retrieval_node",
                tool_call_id=tool_call_id)]
        })

    return
