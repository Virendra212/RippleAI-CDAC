import os
import re
import json
import uuid
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.errors import GraphRecursionError

# ------------ Environment ------------
os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

from util.graph import graph
from util.prompt import system_prompt_ai



# ------------ FastAPI App ------------
app = FastAPI()


app.mount("/postImages", StaticFiles(directory="postImages"), name="postImages")
app.mount("/songs", StaticFiles(directory="songs"), name="songs")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------ Request Model ------------
class GeneratePostsRequest(BaseModel):
    prompt: str

# ------------ Core Logic ------------
async def generate_posts(prompt: str):
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_ai),
        ("human", "{input}")
    ])

    formatted_messages = chat_prompt.format_messages(input=prompt)

    initial_state = {
        "messages": [{"role": m.type, "content": m.content} for m in formatted_messages],
        "output_json": {}
    }

    response_text = ""

    config = RunnableConfig(
        recursion_limit=20,
        configurable={"thread_id": str(uuid.uuid4())}
    )

    response_text = ""
    try:
      for event in graph.stream(initial_state, config=config):
        for node_output in event.values():

            # CASE 1: node_output is a dict
            if isinstance(node_output, dict):
                messages = node_output.get("messages", [])

            # CASE 2: node_output is already a list of messages
            elif isinstance(node_output, list):
                messages = node_output

            else:
                continue

            for msg in messages:
                content = getattr(msg, "content", None)
                if content:
                    response_text += content

    except GraphRecursionError:
        pass

    # ---- Parse JSON safely ----
    try:
        text = response_text.strip()
        text = text.replace("```json", "").replace("```", "").strip()

        match = re.search(r"\[\s*{.*}\s*\]", text, re.DOTALL)
        if not match:
            raise ValueError("JSON not found")

        return json.loads(match.group(0))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate valid post JSON"
        )



# ------------ API Endpoint ------------
@app.post("/ai/generate-posts")
async def generate_posts_api(req: GeneratePostsRequest):
    posts = await generate_posts(req.prompt)
    print(posts)
    return {
        "status": "SUCCESS",
        "posts": posts
    }

# ------------ Run App ------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)