import sys
import os
import io

# Fix Windows terminal encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.transit_route_tool import TransitRouteTool
from dotenv import load_dotenv

load_dotenv(override=True)

def main():
    try:
        tool = TransitRouteTool()
    except ValueError as e:
        print(f"[LOI] {e}")
        print("Hay them GOOGLE_MAPS_API_KEY vao file .env")
        return

    print("== Google Maps Routes API - Transit Route Tool ==")
    print("=" * 50)

    if len(sys.argv) == 3:
        origin = sys.argv[1]
        destination = sys.argv[2]
    else:
        origin = input("Diem xuat phat: ").strip()
        destination = input("Diem den: ").strip()

    print(f"\nDang tim tuyen tu: {origin} --> {destination} ...\n")

    result = tool.find_transit_route(origin, destination)
    print(tool.format_for_display(result))

    if result["success"]:
        print(f"\n[OK] Tim thay {len(result['routes'])} tuyen.")

if __name__ == "__main__":
    main()

