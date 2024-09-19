from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
from chatgpt_interaction import ChatGPTInteraction
import time
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
chat_interaction = ChatGPTInteraction()

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]

class ChatCompletionResponse(BaseModel):
    model: str
    object: str = "chat.completion"
    usage: dict
    id: str
    created: int
    choices: List[dict]

async def verify_api_key(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    api_key = authorization.split(" ")[1]
    try:
        with open('apikeys.txt', 'r') as file:
            api_keys = [key.strip() for key in file.readlines()]
        if api_key not in api_keys:
            raise HTTPException(status_code=401, detail="Invalid API key")
    except FileNotFoundError:
        logger.error("apikeys.txt file not found")
        raise HTTPException(status_code=500, detail="Internal server error")
    return api_key

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest, api_key: str = Depends(verify_api_key)):
    if not request.messages or request.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Invalid messages format")
    
    content = request.messages[-1].content
    try:
        # 使用 asyncio.to_thread 来在后台线程中运行 interact_with_chatgpt
        response_content = await asyncio.to_thread(chat_interaction.interact_with_chatgpt, content)
    except Exception as e:
        logger.exception("An error occurred while interacting with ChatGPT: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
    
    response = ChatCompletionResponse(
        model=request.model,
        usage={
            "prompt_tokens": 25,  # These are placeholder values
            "completion_tokens": 711,
            "total_tokens": 736
        },
        id=f"chatcmpl-{int(time.time())}",
        created=int(time.time()),
        choices=[
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_content
                },
                "finish_reason": "stop"
            }
        ]
    )
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
