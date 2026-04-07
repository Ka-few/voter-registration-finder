from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
from bot import invoke_agent
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

app = FastAPI(title="IEBC Registration Assistant Agent API")

class ChatRequest(BaseModel):
    phone_number: str
    message: str

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.phone_number or not request.message:
        raise HTTPException(status_code=400, detail="Missing phone_number or message")
    
    reply = invoke_agent(request.phone_number, request.message)
    return ChatResponse(reply=reply)

if __name__ == "__main__":
    port = int(os.environ.get("AGENT_PORT", 8000))
    print(f"Starting agent server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
