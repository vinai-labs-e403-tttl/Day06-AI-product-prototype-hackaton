import sys
import io
import os

# Fix Windows terminal encoding for Vietnamese
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ensure backend/app is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from agent.agent import chat

def test_gps_support():
    print("=== Testing GPS and On-trip Support ===")
    
    # 1. Test GPS identification (Royal City coordinates)
    query1 = "Tôi đang ở tọa độ 21.0028, 105.8152, làm sao để đi đến Grand World?"
    print(f"\nQUERY: {query1}")
    response1 = chat(query1)
    print(f"RESPONSE:\n{response1}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. Test On-trip assistance (Asking for next stops on OCT1)
    query2 = "Tôi đang trên xe OCT1, còn mấy trạm nữa thì đến Times City?"
    print(f"\nQUERY: {query2}")
    response2 = chat(query2)
    print(f"RESPONSE:\n{response2}")

if __name__ == "__main__":
    test_gps_support()
