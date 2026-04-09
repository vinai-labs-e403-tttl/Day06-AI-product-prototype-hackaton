from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import sys

# Thêm đường dẫn để import đúng module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app", "agent"))

from agent import chat as agent_chat, clear_conversation

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
    conversation_id: str = "default"


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    reply = agent_chat(request.query, conversation_id=request.conversation_id)
    return ChatResponse(reply=reply)


@app.post("/chat/clear")
async def clear_chat(conversation_id: str = "default"):
    clear_conversation(conversation_id)
    return {"status": "cleared"}
