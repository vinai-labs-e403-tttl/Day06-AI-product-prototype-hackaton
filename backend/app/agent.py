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

TOOLS:
Bạn có các tools sau. Khi cần tìm tuyến bus cụ thể, gọi tool find_bus_route.

Available tools:
- find_bus_route: Tìm tuyến bus giữa hai địa điểm. Args: origin (string), destination (string)"""

    def _get_route_tool(self):
        """Lazy load route tool to avoid import errors if not configured."""
        if self.route_tool is None:
            from app.route_tool import RouteTool
            self.route_tool = RouteTool()
        return self.route_tool

    def get_route_suggestion(self, query: str) -> dict:
        """Process a route query using an agent loop with tool calling."""
        tools = [
            {
                "type": "function",
                "name": "find_bus_route",
                "description": "Tìm tuyến bus giữa hai địa điểm sử dụng Google Maps API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "Địa chỉ hoặc tên điểm đi"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Địa chỉ hoặc tên điểm đến"
                        }
                    },
                    "required": ["origin", "destination"]
                }
            }
        ]

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query}
        ]

        max_iterations = 10
        for _ in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            if message.tool_calls:
                # Agent wants to call a tool
                for tool_call in message.tool_calls:
                    if tool_call.function.name == "find_bus_route":
                        args = json.loads(tool_call.function.arguments)
                        route_result = self._call_route_tool(args["origin"], args["destination"])
                        messages.append(message)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(route_result)
                        })
                    else:
                        # Unknown tool
                        messages.append(message)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": "Unknown tool"})
                        })
                # Continue loop to process tool result
                continue
            else:
                # Final response from agent
                return {
                    "reply": message.content,
                    "suggested_routes": None,
                    "confidence": 0.85,
                }

        # Max iterations reached
        return {
            "reply": "Xin lỗi, tôi cần thêm thời gian để xử lý yêu cầu của bạn. Bạn có thể thử hỏi cụ thể hơn không?",
            "suggested_routes": None,
            "confidence": 0.5,
        }

    def _call_route_tool(self, origin: str, destination: str) -> dict:
        """Call the route tool and format the result."""
        try:
            tool = self._get_route_tool()
            route_result = tool.find_bus_route(origin, destination)
            return route_result
        except Exception as e:
            return {
                "success": False,
                "routes": [],
                "message": f"Lỗi khi tìm tuyến: {str(e)}"
            }

    def _format_route_response(self, route_result: dict, origin: str, destination: str) -> dict:
        """Format Google Maps route result into user-friendly response."""
        route = route_result["routes"][0]
        bus_steps = route["bus_steps"]

        if not bus_steps:
            return {
                "reply": f"Tuyến bus từ {origin} đến {destination} không tìm thấy. Bạn có thể kiểm tra trên bản đồ VinBus.",
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

        reply = f"Tìm được tuyến bus từ {origin} đến {destination}:\n\n"
        reply += f"⏱ {route['total_duration']} · 🚌 {route['total_distance']}\n\n"

        for step in bus_steps:
            reply += f"🚌 Bus {step['bus_number']}: {step['departure_stop']} → {step['arrival_stop']} ({step['num_stops']} trạm, {step['duration']})\n"

        return {
            "reply": reply,
            "suggested_routes": bus_steps,
            "confidence": 0.9,
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
