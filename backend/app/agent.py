import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


class Agent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
        self.route_tool = None  # Lazy load

        self.system_prompt = """Bạn là FlowBot - trợ lý tìm tuyến bus VinBus ở TP.HCM và Hà Nội.

KIỂM TRA TRƯỚC KHI TRẢ LỜI:
- CHỉ gợi ý tuyến bus khi bạn BIẾT chắc tuyến đó tồn tại trong hệ thống VinBus
- Nếu không chắc, trả lời: "Tôi chưa có dữ liệu tuyến này" thay vì bịa ra
- Khi user hỏi "đi từ A đến B", luôn kiểm tra xem A và B có trạm bus gần đó không

TRẢ LỜI:
- Trả lời bằng tiếng Việt, ngắn gọn, thân thiện
- Nếu tìm được tuyến: "Tuyến [số tuyến] đi từ [điểm đi] → [điểm đến]. ⏱ [thời gian] · 💰 [giá vé] · 🚌 [số trạm dừng]"
- Nếu không chắc chắn: gợi 2 tùy chọn và hỏi user chọn
- Nếu không có dữ liệu: nói rõ ràng và suggest mở bản đồ VinBus

TÍNH NĂNG ĐẶC BIỆT:
- Hỗ trợ cả tiếng Anh cho tourists
- Nếu user correction ("Sai tuyến"), ghi nhận để cải thiện

KHI CẦN TÌM TUYẾN CỤ THỂ:
Dùng format JSON để gọi tool:
{
  "tool": "find_bus_route",
  "args": {
    "origin": "địa chỉ hoặc tên điểm đi",
    "destination": "địa chỉ hoặc tên điểm đến"
  }
}"""

    def _get_route_tool(self):
        """Lazy load route tool to avoid import errors if not configured."""
        if self.route_tool is None:
            from app.route_tool import RouteTool
            self.route_tool = RouteTool()
        return self.route_tool

    def get_route_suggestion(self, query: str) -> dict:
        """Process a route query and return suggestion with metadata."""
        # Check for route search intent
        route_keywords = ["đi từ", "từ", "đến", "về", "how do i get", "from", "to", "go to"]
        needs_route_search = any(kw in query.lower() for kw in route_keywords)

        if needs_route_search:
            # Extract origin/destination from query
            extraction = self._extract_locations(query)
            if extraction["origin"] and extraction["destination"]:
                try:
                    tool = self._get_route_tool()
                    route_result = tool.find_bus_route(
                        extraction["origin"],
                        extraction["destination"]
                    )
                    if route_result["success"] and route_result["routes"]:
                        return self._format_route_response(route_result, extraction)
                except Exception:
                    pass  # Fall through to AI response

        # Fallback: use AI response directly
        response = self.client.responses.create(
            model=self.model,
            instructions=self.system_prompt,
            input=query,
        )

        return {
            "reply": response.output_text,
            "suggested_routes": None,
            "confidence": 0.85,
        }

    def _extract_locations(self, query: str) -> dict:
        """Extract origin and destination from natural language query."""
        prompt = f"""Extract origin and destination from this Vietnamese/English query.
Return JSON with 'origin' and 'destination' keys.

Query: {query}

Examples:
- "đi từ Landmark 81 về Quận 1" → {{"origin": "Landmark 81, Ho Chi Minh City", "destination": "District 1, Ho Chi Minh City"}}
- "từ bến thành đến Landmark 81" → {{"origin": "Ben Thanh, Ho Chi Minh City", "destination": "Landmark 81, Ho Chi Minh City"}}
- "how do I get to Central Park" → {{"origin": "current location or unspecified", "destination": "Central Park, Ho Chi Minh City"}}

Return only JSON."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def _format_route_response(self, route_result: dict, extraction: dict) -> dict:
        """Format Google Maps route result into user-friendly response."""
        route = route_result["routes"][0]
        bus_steps = route["bus_steps"]

        if not bus_steps:
            return {
                "reply": f"Tuyến bus từ {extraction['origin']} đến {extraction['destination']} không tìm thấy. Bạn có thể kiểm tra trên bản đồ VinBus.",
                "suggested_routes": [],
                "confidence": 0.3,
            }

        # Format bus info
        bus_info_parts = []
        for step in bus_steps:
            bus_info_parts.append(
                f"Bus {step['bus_number']}: {step['departure_stop']} → {step['arrival_stop']} ({step['num_stops']} trạm dừng)"
            )

        bus_lines = " | ".join([s["bus_number"] for s in bus_steps])

        reply = f"Tìm được tuyến bus từ {extraction['origin']} đến {extraction['destination']}:\n\n"
        reply += f"⏱ {route['total_duration']} · 🚌 {route['total_distance']}\n\n"

        for step in bus_steps:
            reply += f"🚌 Bus {step['bus_number']}: {step['departure_stop']} → {step['arrival_stop']} ({step['num_stops']} trạm, {step['duration']})\n"

        return {
            "reply": reply,
            "suggested_routes": bus_steps,
            "confidence": 0.9,
        }