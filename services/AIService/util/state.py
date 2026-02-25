from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Literal, Annotated
from typing import List

class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str
    
class PostState(TypedDict):
    messages:  Annotated[List[Message], add_messages]
    caption: str                 # output of Node A
    image_ref: str               # URL or path from Node B
    selected_music: str          # identifier from Node C
    output_json: str            # final output from Node D
    scheduling_time: str
