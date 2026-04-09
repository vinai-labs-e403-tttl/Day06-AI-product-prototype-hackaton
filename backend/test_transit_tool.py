import sys
import os
import io

# Fix Windows terminal encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.transit_route_tool import TransitRouteTool
from app.tools.local_route_tool import LocalRouteTool
from dotenv import load_dotenv

load_dotenv(override=True)

def main():
    try:
        transit_tool = TransitRouteTool()
        local_tool = LocalRouteTool()
    except Exception as e:
        print(f"[LOI] {e}")
        return

    print("== FlowBot Transit Test (Hybrid: Local + Google Maps) ==")
    print("=" * 55)

    if len(sys.argv) == 3:
        origin = sys.argv[1]
        destination = sys.argv[2]
    else:
        origin = input("Diem xuat phat: ").strip()
        destination = input("Diem den: ").strip()

    print(f"\nDang tim tuyen tu: {origin} --> {destination} ...\n")

    # 1. Thu tim trong Local DB truoc
    local_result = local_tool.find_route(origin, destination)
    
    # 2. Thu tim trong Google Maps
    google_result = transit_tool.find_transit_route(origin, destination)

    # Hien thi ket qua Local
    if local_result["found"]:
        print("--- [VINBUS LOCAL DB] ---")
        print(local_tool.format_for_display(local_result))
        print("-" * 30)
    else:
        print("--- [VINBUS LOCAL DB]: Khong tim thay tuyen noi khu phu hop. ---")

    # Hien thi ket qua Google Maps
    print("\n--- [GOOGLE MAPS ROUTES API] ---")
    print(transit_tool.format_for_display(google_result))

    if local_result["found"] or google_result["success"]:
        print(f"\n[OK] Da hoan tat tim kiem.")

if __name__ == "__main__":
    main()


