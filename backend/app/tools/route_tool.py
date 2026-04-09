from googlemaps import Client
from langchain_core.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()


class RouteTool:
    """Tool for finding bus routes using Google Maps Directions API."""

    def __init__(self):
        self.client = Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

    def find_bus_route(self, origin: str, destination: str) -> dict:
        """Find bus route between two locations using Google Maps."""
        try:
            directions = self.client.directions(
                origin,
                destination,
                mode="transit",
                transit_mode="bus",
                language="vi"
            )

            if not directions:
                return {
                    "success": False,
                    "routes": [],
                    "message": "Không tìm được tuyến bus cho lộ trình này"
                }

            routes = []
            for route in directions[:3]:  # Top 3 routes
                legs = route["legs"][0]
                steps = [
                    s for s in legs["steps"]
                    if s["travel_mode"] == "TRANSIT" and s.get("transit", {}).get("line", {}).get("vehicle", {}).get("type") == "BUS"
                ]

                bus_steps = []
                for step in steps:
                    transit = step["transit"]
                    bus_line = transit["line"]

                    bus_steps.append({
                        "bus_number": bus_line.get("short_name", bus_line.get("name", "Unknown")),
                        "departure_stop": transit.get("departure_stop", {}).get("name", ""),
                        "arrival_stop": transit.get("arrival_stop", {}).get("name", ""),
                        "num_stops": transit.get("num_stops", 0),
                        "duration": step["duration"]["text"],
                    })

                routes.append({
                    "total_duration": legs["duration"]["text"],
                    "total_distance": legs["distance"]["text"],
                    "bus_steps": bus_steps,
                    "start_address": legs["start_address"],
                    "end_address": legs["end_address"],
                })

            return {
                "success": True,
                "routes": routes,
                "message": None
            }

        except Exception as e:
            return {
                "success": False,
                "routes": [],
                "message": f"Lỗi khi tìm tuyến: {str(e)}"
            }

_route_tool_instance = RouteTool()


@tool
def find_bus_route(origin: str, destination: str) -> dict:
    """Tìm tuyến xe bus từ điểm đi đến điểm đến.

    Args:
        origin: Địa điểm xuất phát (tên địa điểm hoặc địa chỉ, TP.HCM hoặc Hà Nội).
        destination: Địa điểm đến (tên địa điểm hoặc địa chỉ).

    Returns:
        Danh sách tuyến bus phù hợp bao gồm số tuyến, trạm dừng, thời gian di chuyển.
    """
    return _route_tool_instance.find_bus_route(origin, destination)
