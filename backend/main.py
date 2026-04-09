from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os

# Ensure backend/app is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from agent.agent import chat

app = FastAPI(title="FlowBot API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong thực tế nên giới hạn lại
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    location: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    suggested_routes: Optional[list] = []

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    print(f"📩 Nhận yêu cầu: '{request.query}' | Vị trí: {request.location}")
    try:
        reply = chat(request.query, location=request.location)
        return ChatResponse(reply=reply, suggested_routes=[])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
