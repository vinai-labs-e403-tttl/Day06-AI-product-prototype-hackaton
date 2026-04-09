from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import time
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os

# Ensure backend/app is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
from agent.agent import chat, chat_stream
from logger import logger

logger.info("Starting FlowBot API...")

app = FastAPI(title="FlowBot API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong thực tế nên giới hạn lại
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(f"API: {request.method} {request.url.path} - Status: {response.status_code} - Cooldown: {process_time:.2f}ms")
    return response

class ChatRequest(BaseModel):
    query: str
    location: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    suggested_routes: Optional[list] = []

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"📩 Nhận yêu cầu: '{request.query}' | Vị trí: {request.location}")
    try:
        return StreamingResponse(chat_stream(request.query, location=request.location), media_type="application/x-ndjson")
    except Exception as e:
        logger.error(f"❌ Lỗi xử lý chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
