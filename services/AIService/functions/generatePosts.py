import uuid
import re
import json
from fastapi import HTTPException
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.errors import GraphRecursionError
from util.graph import graph
from util.prompt import system_prompt_ai

async def generate_posts(prompt: str):
    # ---- Prepare chat prompt ----
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_ai),
        ("human", "{input}")
    ])

    MAX_MESSAGES = 10  # limit messages to avoid 413 Payload Too Large
    formatted_messages = chat_prompt.format_messages(input=prompt)
    messages = [{"role": m.type, "content": m.content} for m in formatted_messages[-MAX_MESSAGES:]]

    # ---- Shared state for all tools ----
    state = {
        "messages": messages,
        "output_json": True,
        "thread_id": str(uuid.uuid4())
    }

    # ---- Example: selectMusic tool ----
    select_music_input = {
        "caption": "Road Safety Campaign",
        "image_ref": "image1.jpg",
        "state": state,        # ✅ REQUIRED
        "output_json": True,
        "scheduling_time": "",
        "selected_music": ""
    }

    # Call the selectMusic tool
    try:
        music_result = graph.run_tool("selectMusic", **select_music_input)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"selectMusic tool failed: {str(e)}"
        )

    response_text = ""

    config = RunnableConfig(
        recursion_limit=20,
        configurable={"thread_id": state["thread_id"]}
    )

    # ---- Stream the graph ----
    try:
        for event in graph.stream(state, config=config):
            for node_output in event.values():
                # node_output may be a list of dicts
                if isinstance(node_output, list):
                    for msg in node_output:
                        if isinstance(msg, dict) and msg.get("content"):
                            response_text += msg["content"] + "\n"
                # or node_output may be a dict with "messages"
                elif isinstance(node_output, dict) and "messages" in node_output:
                    for msg in node_output["messages"]:
                        if isinstance(msg, dict) and msg.get("content"):
                            response_text += msg["content"] + "\n"

    except GraphRecursionError:
        pass

    # ---- Parse JSON safely ----
    try:
        text = response_text.strip()
        text = text.replace("```json", "").replace("```", "").strip()

        match = re.search(r"\[\s*{.*}\s*\]", text, re.DOTALL)
        if not match:
            raise ValueError("JSON not found in generated content")

        posts = json.loads(match.group(0))
        if not isinstance(posts, list):
            raise ValueError("Parsed JSON is not a list")

        # ---- Example: tavily_search tool (optional) ----
        tavily_input = {
            "query": prompt,
            "topic": "news",
            "start_date": None,
            "end_date": None,
            "time_range": "month",
            "exclude_domains": None,   # must be list or None
            "include_domains": None,   # must be list or None
            "include_images": False,   # must be boolean
            "state": state             # pass the same dict
        }

        # tavily_results = graph.run_tool("tavily_search", **tavily_input)

        return posts

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate valid post JSON: {str(e)}"
        )
