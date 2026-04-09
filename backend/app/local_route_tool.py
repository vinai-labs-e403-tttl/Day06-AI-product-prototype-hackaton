import json
import os
from pathlib import Path


class LocalRouteTool:
    """
    Tool tra cứu tuyến VinBus từ database local.
    Dùng cho các tuyến không có trong Google Maps (OCT1, OCT2, OCP1, OCP2...).
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

        Returns:
            dict với keys: found (bool), routes (list), message (str)
        """
        origin_norm = self._normalize(origin)
        dest_norm = self._normalize(destination)

        matched = []
        for route in self._routes:
            origin_match = self._keyword_match(origin_norm, route["origin_keywords"])
            dest_match = self._keyword_match(dest_norm, route["destination_keywords"])

            # Cũng khớp chiều ngược (tuyến 2 chiều)
            reverse_origin = self._keyword_match(dest_norm, route["origin_keywords"])
            reverse_dest = self._keyword_match(origin_norm, route["destination_keywords"])

            if (origin_match and dest_match) or (reverse_origin and reverse_dest):
                matched.append(self._format_route(route, is_reverse=(reverse_origin and reverse_dest)))

        if matched:
            return {"found": True, "routes": matched, "message": None}
        return {
            "found": False,
            "routes": [],
            "message": f"Không tìm thấy tuyến VinBus nội khu cho lộ trình '{origin}' → '{destination}'",
        }

    def get_route_by_id(self, route_id: str) -> dict | None:
        """Lấy thông tin một tuyến cụ thể theo ID (VD: 'OCT1')."""
        route_id = route_id.upper()
        for route in self._routes:
            if route["id"] == route_id:
                return self._format_route(route)
        return None

    def list_all_routes(self) -> list:
        """Trả về danh sách tất cả tuyến trong database."""
        return [
            {
                "id": r["id"],
                "name": r["full_name"],
                "type": r["type"],
                "frequency": r["frequency_minutes"],
                "is_free": r["is_free"],
            }
            for r in self._routes
        ]

    def search_by_keyword(self, keyword: str) -> list:
        """Tìm tuyến theo từ khóa bất kỳ (tên trạm, khu vực...)."""
        kw = self._normalize(keyword)
        results = []
        for route in self._routes:
            all_keywords = (
                route["origin_keywords"]
                + route["destination_keywords"]
                + [s["name"].lower() for s in route["stops"]]
            )
            if any(kw in k for k in all_keywords):
                results.append(self._format_route(route))
        return results

    def format_for_display(self, result: dict) -> str:
        """Chuyển kết quả thành chuỗi dễ đọc."""
        if not result.get("found"):
            return result.get("message", "Không tìm thấy tuyến.")

        lines = []
        for route in result["routes"]:
            free_text = " [MIEN PHI]" if route["is_free"] else ""
            lines.append(f"\n[{route['id']}] {route['full_name']}{free_text}")
            lines.append(f"  Tan suat: {route['frequency_minutes']} phut/chuyen")
            lines.append(f"  Lo trinh: {route['stop_summary']}")
            lines.append(f"  Mo ta: {route['description']}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize(text: str) -> str:
        """Lowercase + bỏ dấu đơn giản để matching."""
        import unicodedata
        text = text.lower().strip()
        # Giữ nguyên tiếng Việt có dấu, chỉ lowercase
        return text

    @staticmethod
    def _keyword_match(text: str, keywords: list) -> bool:
        """Kiểm tra xem text có chứa bất kỳ keyword nào không."""
        return any(kw in text for kw in keywords)

    @staticmethod
    def _format_route(route: dict, is_reverse: bool = False) -> dict:
        stops = route["stops"]
        if is_reverse:
            stops = list(reversed(stops))
        stop_summary = " → ".join(s["name"] for s in stops)
        return {
            "id": route["id"],
            "full_name": route["full_name"],
            "type": route["type"],
            "operator": route["operator"],
            "frequency_minutes": route["frequency_minutes"],
            "is_free": route["is_free"],
            "description": route["description"],
            "stops": stops,
            "stop_summary": stop_summary,
            "is_reverse": is_reverse,
        }
