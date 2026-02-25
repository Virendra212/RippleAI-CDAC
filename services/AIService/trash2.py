import json
import os
import re
import uuid
from dotenv import load_dotenv
import httpx
from db.database import addToDB
# ------------ Environment ------------
os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from langchain_core.messages import SystemMessage
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.runnables import RunnableConfig

from util.graph import graph
from util.prompt import system_prompt_ai
from langchain_core.prompts.chat import ChatPromptTemplate

import httpx
import uuid
import re
import json
from fastapi import HTTPException
from langgraph.errors import GraphRecursionError




# ------------ FastAPI App ------------
app = FastAPI()
app.mount("/songs", StaticFiles(directory="songs"), name="songs")
app.mount("/postImages", StaticFiles(directory="postImages"), name="postImages")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


system_prompt = SystemMessage(
    content=(system_prompt_ai)
)

class ChatRequest(BaseModel):
    message: str
    

async def generate_posts(req):
    # chat template
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_ai),
        ("human", "{input}")
    ])

    formatted_messages = chat_prompt.format_messages(input=req)

    # initial state
    initial_state = {
        "messages": [{"role": m.type, "content": m.content} for m in formatted_messages],
        "caption": "",
        "image_ref": "",
        "selected_music": "",
        "output_json": {},
        "scheduling_time": {}
    }

    response_text = ""

    config = RunnableConfig(
        recursion_limit=20,
        configurable={"thread_id": str(uuid.uuid4())}
    )

    try:
        for event in graph.stream(initial_state, config=config):
            for node_output in event.values():
                for msg in node_output["messages"]:
                    if hasattr(msg, "content") and msg.content:
                        response_text = msg.content
                        msg.pretty_print()

    except GraphRecursionError:
        if response_text.strip():
            try:
                text = response_text.strip()
                text = text.replace("```json", "").replace("```", "").strip()
                text = text.replace("\\'", "'")

                match = re.search(r"\[\s*{.*}\s*\]", text, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    final_posts = json.loads(json_str)
                    return final_posts

            except Exception:
                pass

        # if nothing usable → return controlled fallback
        return [{
            "caption": "Partial output generated due to recursion limit.",
            "image_ref": "",
            "selected_music": ""
        }]

    # normal parsing path
    try:
        text = response_text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        text = text.replace("\\'", "'")

        match = re.search(r"\[\s*{.*}\s*\]", text, re.DOTALL)
        if not match:
            raise ValueError("Post JSON not found")

        json_str = match.group(0)
        final_posts = json.loads(json_str)
        return final_posts

    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse AI output")


async def send_to_ngo_service(ngo_id, campaign_id, posts):
    #adding additional param
    url = os.getenv("NGO_SERVICE_URL")+f"/ngo/NGOService/receivePosts"

    payload = {
        "ngoId": ngo_id,
        "campaignId": campaign_id,
        "posts": posts
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reach NGO Service: {str(e)}"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"NGO Service error: {response.text}"
        )

    return response.json()



@app.post("/chat")
async def chat(req: ChatRequest, ngo_id: str, campaign_id: str = ""):
    posts = await generate_posts(req)
    ngo_response = await send_to_ngo_service(ngo_id, campaign_id, posts)
    return {
        "message": "Posts generated & sent to NGO Service successfully",
        "ngo_response": ngo_response
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
