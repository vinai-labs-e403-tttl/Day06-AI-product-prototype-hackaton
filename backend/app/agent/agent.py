from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
import os
import sys

# Đảm bảo thư mục app/tools có thể được import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.transit_route_tool import find_transit_route
from tools.local_route_tool import find_local_vinbus_route, get_route_details

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
    input_text = query
    if location:
        input_text = f"{query}\n[Hệ thống: Vị trí của tôi hiện tại là {location}]"

    # 3. Gửi câu hỏi
    result = graph.invoke({"messages": [HumanMessage(content=input_text)]}, config)
    
    return result["messages"][-1].content


# 6. Chat loop
if __name__ == "__main__":
    print("=" * 60)
    print("FlowBot - Trợ lý Tìm Tuyến Xe Bus")
    print("Gõ 'quit' để thoát")
    print("=" * 60)
    
    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break

        print("\nFlowBot đang tìm tuyến...")
        result = graph.invoke({"messages": [("human", user_input)]})
        final = result["messages"][-1]
        print(f"\nFlowBot: {final.content}")