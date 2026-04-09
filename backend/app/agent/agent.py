from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
import os
import sys

# Đảm bảo thư mục app/tools có thể được import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.route_tool import find_bus_route

load_dotenv()

# 1. Đọc System Prompt
_dir = os.path.dirname(__file__)
with open(os.path.join(_dir, "system_prompt.txt"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Khai báo State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Khởi tạo LLM và Tools
tools_list = [find_bus_route]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools_list)

# 4. Agent Node
def agent_node(state: AgentState):
    messages = state["messages"]
    # Thêm System Prompt vào đầu cuộc hội thoại nếu chưa có
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)

    # LOGGING
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"Gọi tool: {tc['name']} ({tc['args']})")
    else:
        print("Trả lời trực tiếp")

    return {"messages": [response]}

# 5. Xây dựng Graph
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)

tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

graph = builder.compile()


def chat(query: str) -> str:
    """Nhận câu hỏi từ user, trả về câu trả lời từ FlowBot."""
    result = graph.invoke({"messages": [("human", query)]})
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