from typing import Annotated
import json
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
import os
import sys
from datetime import datetime
import pytz # Cần thiết để đảm bảo đúng múi giờ Việt Nam

# Đảm bảo thư mục app/tools có thể được import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.transit_route_tool import find_transit_route
from tools.local_route_tool import find_local_vinbus_route, get_route_details
from logger import logger

# Setup state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 1. Load system prompt
prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
with open(prompt_path, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Setup LLM & Tools
tools_list = [find_transit_route, find_local_vinbus_route, get_route_details]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools_list)

# 3. Agent Node
def chatbot_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 4. Build graph
builder = StateGraph(State)
builder.add_node("agent", chatbot_node)
tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

# Compile with memory
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

def chat(query: str, location: str = None, session_id: str = "default-session") -> str:
    """
    Hàm chat chính hỗ trợ bộ nhớ và vị trí.
    """
    config = {"configurable": {"thread_id": session_id}}
    
    # 1. Kiểm tra session mới để gửi System Prompt
    state = graph.get_state(config)
    if not state.values:
        graph.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT)]}, config)

    # 2. Chuẩn bị tin nhắn User
    now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    current_time_str = now.strftime("%H:%M, %A ngày %d/%m/%Y")
    
    input_text = query
    context_prefix = f"[Hệ thống: Thời gian hiện tại là {current_time_str}]"
    if location:
        context_prefix += f"\n[Hệ thống: Vị trí của tôi hiện tại là {location}]"
    
    input_text = f"{context_prefix}\n\n{query}"

    # 3. Gửi câu hỏi
    logger.info(f"🤖 Agent đang xử lý câu hỏi: {query[:50]}...")
    result = graph.invoke({"messages": [HumanMessage(content=input_text)]}, config)
    
    reply = result["messages"][-1].content
    logger.info(f"✅ Agent đã trả lời (độ dài: {len(reply)} ký tự)")
    return reply


def chat_stream(query: str, location: str = None, session_id: str = "default-session"):
    """
    Generator streaming trả về tiến trình suy nghĩ và kết quả cuối cùng.
    """
    config = {"configurable": {"thread_id": session_id}}
    
    # 1. Kiểm tra session mới để gửi System Prompt
    state = graph.get_state(config)
    if not state.values:
        graph.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT)]}, config)

    # 2. Chuẩn bị tin nhắn User
    now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    current_time_str = now.strftime("%H:%M, %A ngày %d/%m/%Y")
    
    input_text = query
    context_prefix = f"[Hệ thống: Thời gian hiện tại là {current_time_str}]"
    if location:
        context_prefix += f"\n[Hệ thống: Vị trí của tôi hiện tại là {location}]"
    
    input_text = f"{context_prefix}\n\n{query}"

    # 3. Stream từng bước (node) của graph
    yield json.dumps({"status": "FlowBot đang phân tích yêu cầu..."}) + "\n"
    
    final_reply = ""
    try:
        for event in graph.stream({"messages": [HumanMessage(content=input_text)]}, config):
            for node_name, node_state in event.items():
                if node_name == "agent":
                    messages = node_state.get("messages", [])
                    if messages:
                        last_msg = messages[-1]
                        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                            yield json.dumps({"status": "FlowBot đang tra cứu dữ liệu tuyến bus..."}) + "\n"
                        else:
                            final_reply = last_msg.content
                            yield json.dumps({"status": "FlowBot đang chuẩn bị câu trả lời..."}) + "\n"
                elif node_name == "tools":
                    yield json.dumps({"status": "FlowBot đang tổng hợp kết quả từ hệ thống..."}) + "\n"
                    # Lưu lại kết quả tool để trích xuất routes nếu cần
                    messages = node_state.get("messages", [])
                    for msg in messages:
                        if hasattr(msg, "content") and "routes" in msg.content:
                            try:
                                # Đơn giản hóa việc trích xuất routes từ text/json của tool
                                pass 
                            except:
                                pass
    except Exception as e:
        logger.error(f"❌ Streaming error: {str(e)}", exc_info=True)
        yield json.dumps({"error": str(e)}) + "\n"
        return

    # 4. Gửi kết quả cuối cùng
    # Đảm bảo có nội dung trả lời
    if not final_reply:
        # Lấy state cuối cùng nếu chưa bắt được trong stream
        final_state = graph.get_state(config)
        if final_state.values.get("messages"):
            final_reply = final_state.values["messages"][-1].content

    yield json.dumps({"reply": final_reply, "suggested_routes": []}) + "\n"


# 6. Chat loop
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("FlowBot - Trợ lý Tìm Tuyến Xe Bus (CLI Mode)")
    logger.info("Gõ 'quit' để thoát")
    logger.info("=" * 60)
    
    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        logger.info("FlowBot đang tìm tuyến...")
        result = graph.invoke({"messages": [("human", user_input)]})
        final = result["messages"][-1]
        print(f"\nFlowBot: {final.content}")