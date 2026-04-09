# FlowBot — VinBus Route Chatbot

**Team 31 · E403 · Track: XanhSM · AI Thực Chiến 2026**

> Người dùng VinBus mất thời gian tìm tuyến bus vì giao diện bản đồ phức tạp — FlowBot trả lời bằng ngôn ngữ tự nhiên, gợi ý tuyến bus phù hợp tại Hà Nội trong vài giây.

---

## Thành viên

| Tên | GitHub |
|-----|--------|
| Đăng Thanh Tùng | [@dang1412](https://github.com/dang1412) |
| Trần Kiên Trường | [@tktrev](https://github.com/tktrev) |
| Trịnh Ngọc Tú | [@cheeka13](https://github.com/cheeka13) |
| Đặng Quang Minh | [@minh267](https://github.com/minh267) |
| Trần Tiến Long | [@longtranvie](https://github.com/longtranvie) |

---

## Demo

User nhập: _"Đi từ Hồ Hoàn Kiếm đến Văn Miếu bằng bus"_
→ FlowBot gọi Google Maps Transit API + local VinBus DB → trả về số tuyến, trạm dừng, thời gian.

```
🚌 Tuyến 23: Hồ Hoàn Kiếm → Văn Miếu
⏱ Thời gian: 12 phút
📍 Khoảng cách: 2.1 km
🔁 Số trạm dừng: 3
```

---

## Cấu trúc repo

```
├── backend/                  # FastAPI + LangGraph agent
│   ├── app/
│   │   ├── agent/            # LangGraph StateGraph + system prompt
│   │   ├── tools/            # Google Maps Transit tool + local route tool
│   │   └── vinbus_local_routes.json
│   ├── main.py               # FastAPI entrypoint
│   └── requirements.txt
├── frontend/                 # React + TypeScript + Vite
│   └── src/
│       └── screens/Chat.tsx  # Chat UI chính
└── docs/
    ├── spec-final.md         # SPEC 6 phần
    └── prototype-readme.md   # Mô tả prototype + phân công
```

---

## Chạy nhanh

```bash
# Backend
cd backend && cp .env.example .env   # điền OPENAI_API_KEY + GOOGLE_MAPS_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload            # → localhost:8000

# Frontend
cd frontend && cp .env.example .env
yarn install && yarn dev             # → localhost:5173
```

---

## Tài liệu

- [SPEC final](docs/spec-final.md) — Canvas, User Stories, Eval, Failure Modes, ROI, Mini Spec
- [Prototype README](docs/prototype-readme.md) — mô tả kỹ thuật + phân công
