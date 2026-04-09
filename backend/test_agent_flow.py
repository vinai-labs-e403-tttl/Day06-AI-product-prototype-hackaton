import sys
import io
import os

# Fix Windows terminal encoding for Vietnamese
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


# Ensure backend/app is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from agent.agent import chat

def interactive_chat():
    print("=" * 60)
    print("FlowBot Test Interface (Cơ chế LangGraph)")
    print("Nhập câu hỏi của bạn (ví dụ: 'Đi từ Bến Thành đến Quận 7')")
    print("Gõ 'quit' hoặc 'exit' để thoát.")
    print("=" * 60)

    while True:
        try:
            query = input("\nBạn: ").strip()
            if not query:
                continue
            if query.lower() in ("quit", "exit", "q"):
                print("Tạm biệt!")
                break

            print("\nFlowBot đang xử lý...")
            response = chat(query)
            print("-" * 30)
            print(f"FlowBot: {response}")
            print("-" * 30)
            
        except KeyboardInterrupt:
            print("\nĐã thoát.")
            break
        except Exception as e:
            print(f"\n[LOI] {e}")

if __name__ == "__main__":
    interactive_chat()

