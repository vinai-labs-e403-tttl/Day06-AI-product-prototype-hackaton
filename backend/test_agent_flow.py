import sys
import io
import os

# Fix Windows terminal encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ensure backend/app is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

try:
    from agent.agent import chat
except ImportError:
    # Fallback for different directory structures
    sys.path.insert(0, os.path.dirname(__file__))
    from app.agent.agent import chat

def interactive_chat():
    print("=" * 60)
    print("      FLOWBOT - AI BUS ASSISTANT (FRONTEND MOCK)      ")
    print("=" * 60)
    print("Hướng dẫn:")
    print("1. Chat bình thường để tìm đường.")
    print("2. Dùng '/loc [tọa độ]' để giả lập GPS (VD: /loc 21.0028, 105.8152)")
    print("3. Gõ 'exit' để thoát.")
    print("-" * 60)

    # Vị trí giả lập (giống như GPS của điện thoại)
    current_location = None

    while True:
        try:
            user_input = input("\nBạn: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ("exit", "quit", "q"):
                print("Tạm biệt!")
                break

            # Xử lý lệnh giả lập GPS tại Frontend Mock
            if user_input.startswith("/loc"):
                parts = user_input.split(" ", 1)
                if len(parts) > 1:
                    current_location = parts[1].strip()
                    print(f"📍 [SYSTEM] Đã kích hoạt GPS giả lập: {current_location}")
                else:
                    current_location = None
                    print("📍 [SYSTEM] Đã tắt GPS.")
                continue

            print("FlowBot đang xử lý...")
            
            # Gửi query VÀ location (nếu có) vào API backend
            response = chat(user_input, location=current_location)
            
            print("-" * 40)
            print(f"FlowBot: {response}")
            print("-" * 40)

        except KeyboardInterrupt:
            print("\nKết thúc.")
            break
        except Exception as e:
            print(f"\n[Lỗi Hệ Thống]: {e}")

if __name__ == "__main__":
    interactive_chat()
