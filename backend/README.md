# VinBus Route Chatbot Backend

Backend này cung cấp API cho chatbot tìm tuyến bus. Mục tiêu của service là:

- nhận câu hỏi ngôn ngữ tự nhiên từ frontend
- trích xuất điểm đi và điểm đến
- tìm tuyến bus bằng Google Maps Transit API
- trả về câu trả lời dạng text cho chatbot

Hiện backend đang là một prototype hackathon, nên có một số phần đang ở trạng thái chuyển tiếp và cần lưu ý khi phát triển tiếp.

## Cấu trúc thư mục

```text
backend/
├─ app/
│  ├─ __init__.py
│  ├─ agent.py
│  └─ route_tool.py
├─ .env
├─ .env.example
├─ main.py
├─ README.md
└─ requirements.txt
```

## Thành phần chính

### `main.py`

Expose FastAPI app và 3 endpoint:

- `GET /`
  Health check
- `POST /chat`
  Nhận câu hỏi chatbot và trả câu trả lời
- `POST /chat/clear`
  Xóa hội thoại theo `conversation_id`

### `app/agent.py`

Agent layer chịu trách nhiệm:

- gọi OpenAI để hiểu query
- gọi tool tìm tuyến bus
- định dạng câu trả lời cuối cùng

Trong file hiện tại có 2 hướng xử lý route:

- Google Maps route tool qua `RouteTool`
- local route tool qua `LocalRouteTool`

Lưu ý:

- `LocalRouteTool` đang được tham chiếu trong code nhưng chưa thấy file tương ứng trong `backend/app`
- phần import trong `main.py` hiện dùng `from agent import chat as agent_chat, clear_conversation`, khác với class `Agent` hiện thấy trong `app/agent.py`
- điều này cho thấy backend đang có dấu hiệu còn sót code cũ và cần đồng bộ lại trước khi dùng production

### `app/route_tool.py`

Route tool dùng Google Maps Directions API với:

- `mode="transit"`
- `transit_mode="bus"`
- `language="vi"`

Tool sẽ:

- gọi Google Maps Directions API
- lọc các bước có `travel_mode = TRANSIT`
- chỉ giữ các bước là `BUS`
- trả về:
  - số tuyến bus
  - trạm lên
  - trạm xuống
  - số trạm
  - thời lượng

## Yêu cầu môi trường

Tạo file `backend/.env` từ `backend/.env.example`:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### Ý nghĩa biến môi trường

- `OPENAI_API_KEY`
  Dùng để gọi model OpenAI cho bước hiểu câu hỏi / orchestration
- `GOOGLE_MAPS_API_KEY`
  Dùng để tìm tuyến bus qua Google Maps Directions API

## Cài đặt

Khuyến nghị dùng Python 3.11.

```powershell
cd backend
py -3.11 -m pip install -r requirements.txt
```

## Chạy local

```powershell
cd backend
py -3.11 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Sau khi chạy, backend sẽ có tại:

- `http://localhost:8000`

## API contract hiện tại

### `GET /`

Response:

```json
{
  "status": "ok"
}
```

### `POST /chat`

Request:

```json
{
  "query": "Đi từ Landmark 81 đến chợ Bến Thành",
  "conversation_id": "default"
}
```

Response hiện tại theo `main.py`:

```json
{
  "reply": "..."
}
```

Lưu ý:

- trong `agent.py` còn xuất hiện logic trả `suggested_routes` và `confidence`
- nhưng `main.py` hiện chưa expose 2 field này trong `ChatResponse`
- nếu frontend cần route cards hoặc confidence score, cần đồng bộ lại response model

### `POST /chat/clear`

Request query param:

```text
/chat/clear?conversation_id=default
```

Response:

```json
{
  "status": "cleared"
}
```

## Luồng xử lý hiện tại

1. Frontend gửi câu hỏi đến `/chat`
2. Backend chuyển query cho agent
3. Agent dùng OpenAI để hiểu yêu cầu
4. Agent gọi route tool để tìm bus route
5. Route tool gọi Google Maps Directions API
6. Backend trả text response cho frontend

## Giới hạn hiện tại

- Phụ thuộc mạnh vào Google Maps Directions API
- Có khả năng không ra tuyến chính xác 100% như dữ liệu vận hành xe buýt thật
- Một phần code vẫn đang pha giữa version cũ và version mới
- `LocalRouteTool` chưa có file thực tế trong repo hiện tại
- `main.py` và `app/agent.py` đang chưa hoàn toàn đồng bộ interface
- README này mô tả đúng trạng thái code hiện có, không giả định những phần chưa tồn tại

## Hướng nâng cấp đề xuất

- Đồng bộ lại `main.py` và `app/agent.py` về một flow duy nhất
- Bổ sung `local_route_tool.py` nếu muốn ưu tiên dữ liệu tuyến nội bộ
- Trả thêm `suggested_routes` và `confidence` từ API để frontend render tốt hơn
- Thay Google-only routing bằng GTFS / GTFS-Realtime nếu muốn sát thực tế hơn
- Thêm logging cho:
  - query gốc
  - origin / destination đã parse
  - route được chọn
  - lỗi từ Google Maps

## Ghi chú cho team

Nếu backend chạy nhưng frontend không hiển thị đúng route:

- kiểm tra file `main.py` có đang import đúng agent không
- kiểm tra `ChatResponse` có khớp với nhu cầu frontend không
- kiểm tra `GOOGLE_MAPS_API_KEY` đã bật Directions API / transit chưa
- kiểm tra có đang tham chiếu tới `LocalRouteTool` mà chưa có file tương ứng hay không
