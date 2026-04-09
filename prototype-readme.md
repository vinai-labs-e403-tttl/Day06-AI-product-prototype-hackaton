# Prototype — FlowBot: VinBus Route Chatbot

## Mô tả

FlowBot là chatbot hội thoại giúp user tìm tuyến xe bus VinBus bằng ngôn ngữ tự nhiên (tiếng Việt và tiếng Anh). User nhập câu hỏi dạng "Đi từ Landmark 81 về Quận 1 thế nào?" → AI phân tích, gọi tool tìm tuyến thật, trả về số tuyến, trạm dừng, thời gian di chuyển — không hallucinate.

## Level: Working Prototype ⚡

Có AI và dữ liệu tuyến thật chạy end-to-end. Input → AI xử lý → output demo live được.

## Luồng hoạt động

```
User nhập câu hỏi (frontend React)
        ↓
POST /chat → FastAPI backend
        ↓
LangGraph Agent (GPT-4o-mini + tool calling)
        ↓
Tool: find_transit_route()
        ├─ Ưu tiên 1: Local VinBus DB (vinbus_local_routes.json)
        └─ Fallback: Google Maps Routes API v2 (transit mode)
        ↓
Trả lời có cấu trúc: số tuyến + trạm dừng + thời gian
        ↓
Hiển thị trong Chat UI (có route cards + loading state)
```

## Links

- **Repo nhóm:** https://github.com/vinai-labs-e403-tttl/Day06-AI-product-prototype-hackaton
- **Backend:** `backend/` — FastAPI + LangGraph agent
- **Frontend:** `frontend/` — React + TypeScript + Vite

> ⚠️ Cần `OPENAI_API_KEY` và `GOOGLE_MAPS_API_KEY` để chạy đầy đủ. Demo local: backend `localhost:8000`, frontend `localhost:5173`.

## Tools và API đã dùng

| Thành phần | Tool / API |
|-----------|-----------|
| LLM | OpenAI GPT-4o-mini (tool calling) |
| Agent framework | LangGraph (StateGraph + ToolNode) |
| Transit data | Google Maps Routes API v2 (TRANSIT mode) |
| Local bus data | `vinbus_local_routes.json` — VinBus OCT1, OCT2, OCP1, OCP2... |
| Backend | FastAPI + Uvicorn |
| Frontend | React + TypeScript + Vite + Framer Motion |

## Phân công

| Thành viên | GitHub | Phần đảm nhận |
|-----------|--------|--------------|
| Đăng Thanh Tùng | dang1412 | Backend agent core (`app/agent/agent.py`), LangGraph setup, system prompt |
| Trần Kiên Trường | tktrev | Google Maps Transit tool (`tools/transit_route_tool.py`), API integration |
| Trịnh Ngọc Tú | cheeka13 | Frontend Chat UI (`screens/Chat.tsx`), UX flow, loading/error states |
| Đặng Quang Minh | minh267 | Local VinBus DB (`vinbus_local_routes.json`, `local_route_tool.py`), route matching |
| Trần Tiến Long | longtranvie | FastAPI backend (`main.py`), CORS config, SPEC + docs |

## Cách chạy

```bash
# Backend
cd backend
cp .env.example .env        # thêm OPENAI_API_KEY và GOOGLE_MAPS_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload   # chạy tại localhost:8000

# Frontend
cd frontend
cp .env.example .env
yarn install
yarn dev                    # chạy tại localhost:5173
```

## AI call thật — minh chứng

File `backend/app/agent/agent.py`: LangGraph agent gọi `find_transit_route` tool thật, kết nối Google Maps Routes API v2. Không mock, không hardcode response.

File `backend/app/tools/transit_route_tool.py`: POST request đến `https://routes.googleapis.com/directions/v2:computeRoutes` với `travelMode: TRANSIT`, parse transit steps thật từ response.

System prompt (`agent/system_prompt.txt`) enforce rule cứng: **"KHÔNG được tự bịa ra số tuyến bus hay thông tin tuyến đường mà không gọi tool."**
