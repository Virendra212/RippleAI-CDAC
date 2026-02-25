from dataclasses import Field
import json
import re
from typing import List, Optional
import uuid
from fastapi import HTTPException
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.errors import GraphRecursionError
from pydantic import BaseModel
from util.graph import graph
from util.prompt import system_prompt_ai


from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class PostAnalysisRequest(BaseModel):
    caption: str = Field(...)       # just required
    postLink: str
    musicLink: Optional[str] = None

    # Validator for caption length
    @field_validator("caption")
    def check_caption_length(cls, v):
        if len(v) > 1000:
            raise ValueError("Caption must be at most 1000 characters")
        return v


class PostAnalysisResponse(BaseModel):
    positivity: str  
    rank: int        
    reasons: List[str]

    
async def analyze_post_content(post: PostAnalysisRequest) -> PostAnalysisResponse:
    analysis_prompt = f"""
                            Analyze the following social media post strictly for:
                            - positivity
                            - healthy promotion
                            - social welfare impact

                            Penalize heavily if content contains:
                            - abusive language
                            - hate speech
                            - misinformation
                            - harmful or misleading post

                            Give:
                            1. Overall sentiment: POSITIVE / NEUTRAL / NEGATIVE
                            2. Rank out of 10 (integer only)
                            3. Short reasons (bullet points)

                            Post content:
                            Caption: {post.caption}
                            Post Link: {post.postLink}
                            Music Link: {post.musicLink}
                            """

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_ai),
        ("human", "{input}")
    ])

    formatted = chat_prompt.format_messages(input=analysis_prompt)

    state = {
        "messages": [{"role": m.type, "content": m.content} for m in formatted],
        "output_json": {}
    }

    response_text = ""

    config = RunnableConfig(
        recursion_limit=10,
        configurable={"thread_id": str(uuid.uuid4())}
    )

    try:
        for event in graph.stream(state, config=config):
            for node_output in event.values():
                for msg in node_output["messages"]:
                    if msg.content:
                        response_text = msg.content
    except GraphRecursionError:
        pass

    # ---- Extract structured output ----
    try:
        text = response_text.strip()
        text = text.replace("```json", "").replace("```", "").strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("JSON not found")

        data = json.loads(match.group(0))

        return PostAnalysisResponse(
            positivity=data.get("positivity", "NEUTRAL"),
            rank=int(data.get("rank", 5)),
            reasons=data.get("reasons", [])
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze post"
        )
