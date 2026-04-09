import sys
import os

# Thêm thư mục hiện tại vào sys.path để có thể import từ app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.agent import Agent
from dotenv import load_dotenv

def main():
    # Load environment variables từ file .env
    load_dotenv(override=True)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  CẢNH BÁO: Chưa tìm thấy OPENAI_API_KEY trong file .env")
        print("Vui lòng tạo file .env từ .env.example và điền API Key của bạn.")
    
    try:
        print("🤖 Đang khởi tạo FlowBot Agent...")
        agent = Agent()
        print("✅ Khởi tạo thành công! Bạn có thể bắt đầu chat (gõ 'exit' hoặc 'quit' để thoát).")
        print("-" * 50)
        
        while True:
            try:
                query = input("\n👤 Bạn: ")
            except EOFError:
                break
                
            if query.lower() in ["exit", "quit", "thoát"]:
                print("👋 Tạm biệt!")
                break
            
            if not query.strip():
                continue
                
            print("⏳ FlowBot đang suy nghĩ...")
            result = agent.get_route_suggestion(query)
            
            print(f"\n🤖 FlowBot: {result['reply']}")
            if result.get('confidence'):
                print(f"📊 Độ tin cậy: {result['confidence'] * 100:.1f}%")
                
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    main()
