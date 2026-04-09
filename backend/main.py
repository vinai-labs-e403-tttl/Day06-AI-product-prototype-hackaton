from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import sys

# Thêm đường dẫn để import đúng module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app", "agent"))

from agent import chat as agent_chat

load_dotenv()

app = FastAPI(title="VinBus Route Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    user_id: str | None = None


class ChatResponse(BaseModel):
    reply: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    reply = agent_chat(request.query)
    return ChatResponse(reply=reply)
