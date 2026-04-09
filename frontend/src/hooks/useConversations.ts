import { useState, useEffect, useCallback } from "react";
import { ChatMessage, Conversation } from "../types";

const STORAGE_KEY = "flowbot_conversations";

const WELCOME_MESSAGE = (id: string): ChatMessage => ({
  id,
  text: "Xin chào! Tôi là FlowBot - trợ lý tìm tuyến bus VinBus. Bạn muốn đi đâu hôm nay?",
  sender: "bot",
  timestamp: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
});

function generateId() {
  return `session_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
}

function createNewConversation(): Conversation {
  const id = generateId();
  return {
    id,
    title: "Cuộc trò chuyện mới",
    createdAt: Date.now(),
    updatedAt: Date.now(),
    messages: [WELCOME_MESSAGE(`welcome_${id}`)],
  };
}

function loadFromStorage(): Conversation[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as Conversation[];
  } catch {
    return [];
  }
}

function saveToStorage(conversations: Conversation[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations));
}

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>(() => {
    const stored = loadFromStorage();
    if (stored.length > 0) return stored;
    const first = createNewConversation();
    return [first];
  });

  const [activeId, setActiveId] = useState<string>(() => {
    const stored = loadFromStorage();
    return stored.length > 0 ? stored[0].id : conversations[0]?.id ?? "";
  });

  // Persist mỗi khi conversations thay đổi
  useEffect(() => {
    saveToStorage(conversations);
  }, [conversations]);

  const activeConversation = conversations.find((c) => c.id === activeId) ?? conversations[0];

  const addNewConversation = useCallback(() => {
    const conv = createNewConversation();
    setConversations((prev) => [conv, ...prev]);
    setActiveId(conv.id);
    return conv;
  }, []);

  const switchConversation = useCallback((id: string) => {
    setActiveId(id);
  }, []);

  const deleteConversation = useCallback(
    (id: string) => {
      setConversations((prev) => {
        const next = prev.filter((c) => c.id !== id);
        if (next.length === 0) {
          const conv = createNewConversation();
          setActiveId(conv.id);
          return [conv];
        }
        if (id === activeId) {
          setActiveId(next[0].id);
        }
        return next;
      });
    },
    [activeId]
  );

  const updateMessages = useCallback(
    (messages: ChatMessage[]) => {
      setConversations((prev) =>
        prev.map((c) => {
          if (c.id !== activeId) return c;
          // Auto-title: lấy text câu hỏi đầu tiên của user
          const firstUserMsg = messages.find((m) => m.sender === "user");
          const title = firstUserMsg
            ? firstUserMsg.text.slice(0, 40) + (firstUserMsg.text.length > 40 ? "…" : "")
            : c.title;
          return { ...c, messages, title, updatedAt: Date.now() };
        })
      );
    },
    [activeId]
  );

  return {
    conversations,
    activeConversation,
    activeId,
    addNewConversation,
    switchConversation,
    deleteConversation,
    updateMessages,
  };
}
