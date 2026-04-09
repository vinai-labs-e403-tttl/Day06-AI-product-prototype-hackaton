import json
import os
import math
import re
from pathlib import Path
from langchain_core.tools import tool
try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class LocalRouteTool:
    """
    Tool tra cứu tuyến VinBus từ database local.
    Hỗ trợ cả tìm kiếm theo từ khóa và tọa độ GPS (Lat, Lng).
    """

    def __init__(self):
        data_path = Path(__file__).parent / "vinbus_local_routes.json"
        with open(data_path, encoding="utf-8") as f:
            self._data = json.load(f)
        self._routes = self._data["routes"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find_route(self, origin: str, destination: str) -> dict:
        """
         Tìm tuyến phù hợp từ database local.
        Hỗ trợ nhận dạng tọa độ "lat,lng" cho điểm đi/đến.
        """
        logger.debug(f"🔍 Đang tìm tuyến VinBus local: {origin} -> {destination}")
        actual_origin = origin
        actual_dest = destination
        origin_stop_info = None

        # 1. Xử lý tọa độ nếu có
        origin_coords = self._parse_coords(origin)
        if origin_coords:
            nearest = self.find_nearest_stop(origin_coords[0], origin_coords[1])
            actual_origin = nearest["name"]
            origin_stop_info = nearest

        dest_coords = self._parse_coords(destination)
        if dest_coords:
            nearest = self.find_nearest_stop(dest_coords[0], dest_coords[1])
            actual_dest = nearest["name"]
            logger.debug(f"📍 Tọa độ đích -> Trạm gần nhất: {actual_dest}")

        # 2. Xử lý trường hợp chỉ có điểm đi (để xác nhận vị trí)
        if not destination or destination.strip() == "":
            if origin_stop_info:
                return {
                    "found": True,
                    "routes": [],
                    "current_location_context": {
                        "nearest_stop": origin_stop_info["name"],
                        "distance_m": round(origin_stop_info["distance_m"]),
                    },
                    "message": f"Tôi đã xác nhận vị trí của bạn tại trạm **{origin_stop_info['name']}**. Bạn muốn đi đến đâu?"
                }
            return {"found": False, "message": "Bạn muốn tìm đường đến đâu?"}

        # 3. Matching theo từ khóa (như cũ)
        origin_norm = self._normalize(actual_origin)
        dest_norm = self._normalize(actual_dest)

        matched = []
        for route in self._routes:
            origin_match = self._keyword_match(origin_norm, route["origin_keywords"])
            dest_match = self._keyword_match(dest_norm, route["destination_keywords"])

            reverse_origin = self._keyword_match(dest_norm, route["origin_keywords"])
            reverse_dest = self._keyword_match(origin_norm, route["destination_keywords"])

            if (origin_match and dest_match) or (reverse_origin and reverse_dest):
                route_info = self._format_route(route, is_reverse=(reverse_origin and reverse_dest))
                if origin_stop_info:
                    route_info["current_location_context"] = {
                        "nearest_stop": origin_stop_info["name"],
                        "distance_m": round(origin_stop_info["distance_m"]),
                        "note": f"Bạn đang ở gần trạm {origin_stop_info['name']} ({round(origin_stop_info['distance_m'])}m)"
                    }
                matched.append(route_info)

        if matched:
            logger.info(f"✅ Tìm thấy {len(matched)} tuyến VinBus local")
            return {"found": True, "routes": matched, "message": None}
        
        return {
            "found": False,
            "routes": [],
            "message": f"Không tìm thấy tuyến VinBus cho '{actual_origin}' → '{actual_dest}'",
        }

    def find_nearest_stop(self, lat: float, lng: float, route_id: str = None) -> dict:
        """Tìm trạm gần nhất dựa trên tọa độ."""
        min_dist = float('inf')
        nearest_stop = None

        routes_to_check = self._routes
        if route_id:
            routes_to_check = [r for r in self._routes if r["id"] == route_id.upper()]

        for route in routes_to_check:
            all_stops = route.get("stops_outbound", []) + route.get("stops_return", [])
            for stop in all_stops:
                if "coords" not in stop:
                    continue
                d = self._haversine(lat, lng, stop["coords"]["lat"], stop["coords"]["lng"])
                if d < min_dist:
                    min_dist = d
                    nearest_stop = {
                        "name": stop["name"],
                        "order": stop["order"],
                        "route_id": route["id"],
                        "distance_m": d
                    }
        
        # Nếu trạm gần nhất xa quá 2km, coi như không nằm trong vùng phủ sóng VinBus local
        if nearest_stop and nearest_stop["distance_m"] > 2000:
            return {
                "name": "Ngoài phạm vi VinBus nội khu", 
                "distance_m": nearest_stop["distance_m"],
                "status": "too_far"
            }
            
        return nearest_stop or {"name": "Không tìm thấy trạm gần đây", "distance_m": 0, "status": "not_found"}

    def get_route_info(self, route_id: str) -> dict | None:
        """Lấy thông tin chi tiết các trạm của một tuyến."""
        route_id = route_id.upper()
        for route in self._routes:
            if route["id"] == route_id:
                return {
                    "id": route["id"],
                    "name": route["full_name"],
                    "stops_outbound": [s["name"] for s in route.get("stops_outbound", [])],
                    "stops_return": [s["name"] for s in route.get("stops_return", [])],
                    "description": route["description"],
                    "operating_hours": route.get("operating_hours"),
                    "frequency_minutes": route.get("frequency_minutes"),
                    "is_free": route.get("is_free", False)
                }
        return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        """Tính khoảng cách giữa 2 điểm (mét)."""
        R = 6371000  # Bán kính Trái Đất mét
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    @staticmethod
    def _parse_coords(text: str):
        """Kiểm tra nếu text là tọa độ 'lat, lng' hoặc có prefix '/loc'."""
        clean_text = text.strip()
        if clean_text.startswith("/loc "):
            clean_text = clean_text[5:].strip()
            
        match = re.match(r"^(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)$", clean_text)
        if match:
            return float(match.group(1)), float(match.group(2))
        return None

    @staticmethod
    def _normalize(text: str) -> str:
        return text.lower().strip()

    @staticmethod
    def _keyword_match(text: str, keywords: list) -> bool:
        return any(kw in text for kw in keywords)

    @staticmethod
    def _format_route(route: dict, is_reverse: bool = False) -> dict:
        stops_list = route.get("stops_outbound", []) if not is_reverse else route.get("stops_return", [])
        stop_summary = " → ".join(s["name"] for s in stops_list)
        return {
            "id": route["id"],
            "full_name": route["full_name"],
            "frequency_minutes": route["frequency_minutes"],
            "is_free": route["is_free"],
            "description": route["description"],
            "stop_summary": stop_summary,
            "stops": stops_list
        }


_local_tool_instance = LocalRouteTool()


@tool
def find_local_vinbus_route(origin: str, destination: str) -> dict:
    """Tra cứu các tuyến VinBus nội khu (OCT1, OCT2, OCP1, OCP2...).
    Hỗ trợ điểm đi/đến bằng tên trạm hoặc tọa độ GPS (dạng 'lat,lng').
    """
    return _local_tool_instance.find_route(origin, destination)


@tool
def get_route_details(route_id: str) -> dict:
    """Lấy danh sách các trạm dừng chi tiết của một tuyến VinBus (VD: 'OCT1').
    Hữu ích khi người dùng muốn biết xe đi qua những đâu hoặc kiểm tra trạm tiếp theo.
    """
    info = _local_tool_instance.get_route_info(route_id)
    if info:
        return {"success": True, "data": info}
    return {"success": False, "message": f"Không tìm thấy tuyến {route_id}"}

