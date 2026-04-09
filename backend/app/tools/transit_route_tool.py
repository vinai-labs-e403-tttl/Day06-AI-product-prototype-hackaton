import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

load_dotenv(override=True)

ROUTES_API_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"

# Field mask: lấy các trường cần thiết cho transit
FIELD_MASK = ",".join([
    "routes.legs.steps.transitDetails",
    "routes.legs.steps.travelMode",
    "routes.legs.steps.startLocation",
    "routes.legs.steps.endLocation",
    "routes.legs.duration",
    "routes.legs.distanceMeters",
    "routes.legs.startLocation",
    "routes.legs.endLocation",
    "routes.localizedValues",
])


class TransitRouteTool:
    """Tool tìm đường bằng phương tiện công cộng dùng Google Maps Routes API v2."""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY chưa được cấu hình trong .env")

    def find_transit_route(
        self,
        origin: str,
        destination: str,
        transit_mode: str = "BUS",          # BUS | SUBWAY | TRAIN | LIGHT_RAIL | RAIL
        routing_preference: str = "LESS_WALKING",  # LESS_WALKING | FEWER_TRANSFERS
        compute_alternatives: bool = True,
    ) -> dict:
        """
        Tìm tuyến đường công cộng từ origin đến destination.

        Args:
            origin: Địa chỉ hoặc tên địa điểm xuất phát
            destination: Địa chỉ hoặc tên địa điểm đến
            transit_mode: Loại phương tiện ưu tiên (BUS, SUBWAY, TRAIN, ...)
            routing_preference: Tùy chọn đường (LESS_WALKING | FEWER_TRANSFERS)
            compute_alternatives: Tìm nhiều tuyến thay thế (mặc định: True)

        Returns:
            dict với keys: success, routes, message
        """
        logger.info(f"🌐 Đang gọi Google Maps Transit API: {origin} -> {destination}")
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        }

        payload = {
            "origin": {"address": origin},
            "destination": {"address": destination},
            "travelMode": "TRANSIT",
            "computeAlternativeRoutes": compute_alternatives,
            "transitPreferences": {
                "allowedTravelModes": [transit_mode],
                "routingPreference": routing_preference,
            },
            "languageCode": "vi",  # Trả lời bằng tiếng Việt
        }

        try:
            response = requests.post(ROUTES_API_URL, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "routes" not in data or not data["routes"]:
                logger.warning(f"⚠️ Google Maps không tìm thấy tuyến: {origin} -> {destination}")
                return {
                    "success": False,
                    "routes": [],
                    "message": "Không tìm được tuyến công cộng cho lộ trình này.",
                }
            
            logger.info(f"✅ Google Maps tìm thấy {len(data['routes'])} tuyến")

            routes = []
            for route in data["routes"]:
                legs = route.get("legs", [{}])[0]
                steps = legs.get("steps", [])

                transit_steps = []
                for step in steps:
                    if step.get("travelMode") != "TRANSIT":
                        continue

                    td = step.get("transitDetails", {})
                    stop_details = td.get("stopDetails", {})
                    transit_line = td.get("transitLine", {})
                    vehicle = transit_line.get("vehicle", {})
                    localized = td.get("localizedValues", {})

                    transit_steps.append({
                        "vehicle_type": vehicle.get("type", "TRANSIT"),
                        "vehicle_name": vehicle.get("name", {}).get("text", ""),
                        "line_name": transit_line.get("name", ""),
                        "line_short_name": transit_line.get("nameShort", ""),
                        "headsign": td.get("headsign", ""),
                        "stop_count": td.get("stopCount", 0),
                        "departure_stop": stop_details.get("departureStop", {}).get("name", ""),
                        "arrival_stop": stop_details.get("arrivalStop", {}).get("name", ""),
                        "departure_time": localized.get("departureTime", {}).get("time", {}).get("text", ""),
                        "arrival_time": localized.get("arrivalTime", {}).get("time", {}).get("text", ""),
                        "agency": transit_line.get("agencies", [{}])[0].get("name", "") if transit_line.get("agencies") else "",
                    })

                # Tổng thời gian và khoảng cách
                duration_seconds = int(legs.get("duration", "0s").replace("s", ""))
                distance_meters = legs.get("distanceMeters", 0)

                routes.append({
                    "transit_steps": transit_steps,
                    "total_duration_minutes": round(duration_seconds / 60),
                    "total_distance_km": round(distance_meters / 1000, 1),
                    "start_address": legs.get("startLocation", {}).get("latLng", {}),
                    "end_address": legs.get("endLocation", {}).get("latLng", {}),
                })

            return {
                "success": True,
                "routes": routes,
                "message": None,
            }

        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = response.json().get("error", {}).get("message", str(e))
            except Exception:
                error_detail = str(e)
            return {
                "success": False,
                "routes": [],
                "message": f"Lỗi HTTP từ API: {error_detail}",
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "routes": [],
                "message": "Timeout khi gọi Google Maps Routes API.",
            }
        except Exception as e:
            logger.error(f"❌ Lỗi khi tìm tuyến Google Maps: {str(e)}", exc_info=True)
            return {
                "success": False,
                "routes": [],
                "message": f"Lỗi khi tìm tuyến: {str(e)}",
            }

    def format_for_display(self, result: dict) -> str:
        """Chuyển kết quả thành chuỗi dễ đọc để hiển thị."""
        if not result["success"]:
            return f"❌ {result['message']}"

        lines = []
        for i, route in enumerate(result["routes"], 1):
            lines.append(f"\n📍 Tuyến {i} | ⏱ {route['total_duration_minutes']} phút | 📏 {route['total_distance_km']} km")
            if not route["transit_steps"]:
                lines.append("  ⚠️ Không có bước đi bằng phương tiện công cộng")
                continue
            for step in route["transit_steps"]:
                vehicle_icon = {"BUS": "🚌", "SUBWAY": "🚇", "TRAIN": "🚆", "LIGHT_RAIL": "🚋"}.get(step["vehicle_type"], "🚍")
                line_display = step["line_short_name"] or step["line_name"]
                lines.append(
                    f"  {vehicle_icon} {line_display} ({step['agency']}) | "
                    f"{step['departure_stop']} → {step['arrival_stop']} | "
                    f"{step['stop_count']} trạm | "
                    f"{step['departure_time']} → {step['arrival_time']}"
                )
        return "\n".join(lines) if lines else "Không tìm được tuyến nào."


_transit_tool_instance = TransitRouteTool()


@tool
def find_transit_route(origin: str, destination: str) -> dict:
    """Tìm tuyến xe bus / phương tiện công cộng từ điểm đi đến điểm đến.

    Args:
        origin: Địa điểm xuất phát (tên địa điểm hoặc địa chỉ, TP.HCM hoặc Hà Nội).
        destination: Địa điểm đến (tên địa điểm hoặc địa chỉ).

    Returns:
        Danh sách các tuyến phù hợp bao gồm số tuyến, trạm dừng, thời gian di chuyển.
    """
    return _transit_tool_instance.find_transit_route(origin, destination)
