
from agent.getInfoFromAnalyticsAI import getInfoFromAnalyticsAI
from agent.getKnowledgeFromStore import getKnowledgeFromStore
from agent.selectMusicTool import selectMusic
from agent.websearchForBestContent import websearch
from agent.GenerateCaptionTool import generateCaption
from agent.GenerateImageTool import generatePostImage


tools = [
            #getKnowledgeFromStore ,
            websearch,
           # getInfoFromAnalyticsAI,
           # generateCaption, 
            generatePostImage,
            selectMusic
]



 #Goal - find trending content around 
      # will use knowledge base 
      # will use web search 
      # will observe that ngos previous posts thier likes and comments statistics 
      # based on all generate a caption and multiple prompts for image generation and music selection based on caption
      