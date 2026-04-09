from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from app.agent import Agent

load_dotenv()

app = FastAPI(title="VinBus Route Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = Agent()


class ChatRequest(BaseModel):
    query: str
    user_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    suggested_routes: list[dict] | None = None
    confidence: float | None = None


@app.get("/")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = agent.get_route_suggestion(request.query)
    return ChatResponse(**result)