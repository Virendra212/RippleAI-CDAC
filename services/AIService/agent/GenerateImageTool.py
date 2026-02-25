import time
from typing import Annotated
import requests
from langchain.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from util.state import PostState
import os
import uuid

# Image generation endpoint
url = "https://api.freepik.com/v1/ai/gemini-2-5-flash-image-preview"
image_api_key = os.getenv("FREE_PIK_KEY_IMAGE")
STATIC_BASE_URL = os.getenv("STATIC_BASE_URL_IMG")
STATIC_DIR = os.getenv("STATIC_DIR") 


@tool
def generatePostImage(
        state: PostState,
        tool_call_id: Annotated[str, InjectedToolCallId],
        query: str = ""
    ) -> Command:
    """Generate an image, save locally, and return static URL."""
    try:
        # Get prompt
        prompt = query or state.get("messages", [{}])[0].get("content", "")
        if not prompt:
            return Command(update={
                "messages": [ToolMessage(
                    content="No prompt found to generate image.",
                    name="image_generation_node",
                    tool_call_id=tool_call_id)]
            })

        # Create task
        payload = {"prompt": prompt}
        headers = {
            "x-freepik-api-key": image_api_key,
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        try:
            res = response.json()
        except Exception:
            return Command(update={
                "messages": [ToolMessage(
                    content="Invalid API response format.",
                    name="image_generation_node",
                    tool_call_id=tool_call_id)]
            })

        # Get task ID
        task_id = res.get("data", {}).get("task_id")
        if not task_id:
            return Command(update={
                "messages": [ToolMessage(
                    content=f"Task creation failed: {res}",
                    name="image_generation_node",
                    tool_call_id=tool_call_id)]
            })

        # Polling
        poll_url = f"{url}/{task_id}"
        poll_headers = {"x-freepik-api-key": image_api_key}

        while True:
            poll_res = requests.get(poll_url, headers=poll_headers).json()
            status = poll_res.get("data", {}).get("status")

            if status == "COMPLETED":

                # DEBUG print
                import json
                print("DEBUG POLL RESPONSE:")
                print(json.dumps(poll_res, indent=4))

                data = poll_res.get("data", {})

                # Extract image from `generated`
                generated_list = data.get("generated", [])
                if not generated_list or not isinstance(generated_list, list):
                    return Command(update={
                        "messages": [ToolMessage(
                            content=f"Image URL missing. RAW RESPONSE: {poll_res}",
                            name="image_generation_node",
                            tool_call_id=tool_call_id)]
                    })

                image_url = generated_list[0]

                # Download image
                img_response = requests.get(image_url)
                ext = ".png"
                filename = f"{uuid.uuid4()}{ext}"
                file_path = os.path.join(STATIC_DIR, filename)

                with open(file_path, "wb") as f:
                    f.write(img_response.content)

                static_url = f"{STATIC_BASE_URL}/{filename}"

                return Command(update={
                    "messages": [ToolMessage(
                        content=f"Image generated successfully.\nURL: {static_url}",
                        name="image_generation_node",
                        tool_call_id=tool_call_id)]
                })


            if status in ["FAILED", "ERROR"]:
                return Command(update={
                    "messages": [ToolMessage(
                        content=f"Image generation failed: {poll_res}",
                        name="image_generation_node",
                        tool_call_id=tool_call_id)]
                })

            time.sleep(2)

    except Exception as e:
        return Command(update={
            "messages": [ToolMessage(
                content=f"Error: {str(e)}",
                name="image_generation_node",
                tool_call_id=tool_call_id)]
        })
