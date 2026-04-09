import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { motion } from "motion/react";
import { Send, Mic, Cpu, Radio, ChevronRight, LocateFixed, Loader2, History } from "lucide-react";
import { ChatMessage, Route } from "../types";
import { cn } from "../lib/utils";
import { useConversations } from "../hooks/useConversations";
import ConversationSidebar from "../components/ConversationSidebar";

interface ChatProps {
  onSelectRoute: (routeId: string) => void;
}

export default function Chat({ onSelectRoute }: ChatProps) {
  const {
    conversations,
    activeConversation,
    activeId,
    addNewConversation,
    switchConversation,
    deleteConversation,
    updateMessages,
  } = useConversations();

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const messages = activeConversation?.messages ?? [];

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Reset input khi đổi conversation
  useEffect(() => {
    setInput("");
    setIsLoading(false);
  }, [activeId]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: input,
      sender: "user",
      timestamp: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
    };

    const newMessages = [...messages, userMessage];
    updateMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input, conversation_id: activeId }),
      });

      const data = await response.json();

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: data.reply || "Xin lỗi, tôi chưa hiểu ý bạn. Bạn có thể diễn đạt lại được không?",
        sender: "bot",
        timestamp: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
        routes: data.suggested_routes?.map((r: any, i: number) => ({
          id: r.bus_number || `route-${i}`,
          name: `BUS ${r.bus_number || "?"}`,
          eta: r.duration || "N/A",
          gate: `${r.departure_stop} → ${r.arrival_stop}`,
          isLive: false,
        })) as Route[],
      };

      updateMessages([...newMessages, botMessage]);
    } catch {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: "Xin lỗi, tôi đang gặp sự cố kết nối. Bạn có thể thử lại được không?",
        sender: "bot",
        timestamp: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
      };
      updateMessages([...newMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      <ConversationSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        conversations={conversations}
        activeId={activeId}
        onSelect={switchConversation}
        onNew={() => { addNewConversation(); setSidebarOpen(false); }}
        onDelete={deleteConversation}
      />

      <main className="max-w-4xl mx-auto px-4 pt-6 pb-32">
        {/* Conversation title bar */}
        <div className="flex items-center gap-3 mb-6 px-1">
          <button
            onClick={() => setSidebarOpen(true)}
            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-surface-container-low hover:bg-surface-container-high transition-colors"
          >
            <History size={16} className="text-primary" />
            <span className="text-sm font-semibold text-on-surface-variant">Lịch sử</span>
          </button>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-primary truncate">{activeConversation?.title}</p>
          </div>
          <button
            onClick={() => addNewConversation()}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-primary text-white text-sm font-bold hover:bg-primary/90 active:scale-95 transition-all"
          >
            + Mới
          </button>
        </div>

        <div className="space-y-8 pb-12">
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                "flex flex-col space-y-2",
                msg.sender === "user" ? "items-end" : "items-start"
              )}
            >
              {msg.sender === "bot" && (
                <div className="flex items-center gap-3 mb-1">
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                    <Cpu className="text-white" size={14} />
                  </div>
                  <span className="font-headline font-bold text-sm tracking-tight text-primary">FlowBot</span>
                </div>
              )}
              <div
                className={cn(
                  "max-w-[85%] md:max-w-[70%] px-6 py-4 shadow-sm",
                  msg.sender === "user" ? "chat-bubble-sender" : "chat-bubble-receiver"
                )}
              >
                <p className="text-[16px] leading-relaxed whitespace-pre-wrap">{msg.text}</p>
              </div>
              <span className="text-xs font-sans uppercase tracking-widest text-outline">
                {msg.sender === "user" ? `Sent ${msg.timestamp}` : msg.timestamp}
              </span>

              {/* Route Results */}
              {msg.routes && msg.routes.length > 0 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                  className="w-full max-w-md grid grid-cols-2 gap-3 mt-4"
                >
                  {msg.routes.map((route) => (
                    <div
                      key={route.id}
                      onClick={() => onSelectRoute(route.id)}
                      className={cn(
                        "col-span-2 md:col-span-1 p-5 rounded-xl cursor-pointer transition-all active:scale-95",
                        route.isLive
                          ? "bg-white border-l-4 border-secondary shadow-sm"
                          : "bg-surface-container-low hover:bg-surface-container-high"
                      )}
                    >
                      <div className="flex justify-between items-start mb-4">
                        <span
                          className={cn(
                            "px-3 py-1 rounded-full text-[10px] font-black tracking-widest",
                            route.isLive
                              ? "bg-secondary-container text-white"
                              : "bg-surface-container-highest text-on-surface-variant"
                          )}
                        >
                          {route.name}
                        </span>
                        {route.isLive && (
                          <span className="flex items-center gap-1 text-secondary font-bold text-[10px]">
                            <Radio size={12} />
                            LIVE
                          </span>
                        )}
                      </div>
                      <h3 className="font-headline font-bold text-xl mb-1">{route.eta}</h3>
                      <p className="text-xs text-outline font-sans uppercase tracking-tight">{route.gate}</p>
                    </div>
                  ))}

                  {/* Map Context Card */}
                  <div className="col-span-2 h-48 rounded-xl overflow-hidden relative group cursor-pointer">
                    <img
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                      src="https://picsum.photos/seed/map-context/600/300"
                      alt="Map Context"
                      referrerPolicy="no-referrer"
                    />
                    <div className="absolute inset-0 bg-linear-to-t from-primary/40 to-transparent"></div>
                    <div className="absolute bottom-4 left-4 right-4 flex justify-between items-center bg-white/90 backdrop-blur-md p-3 rounded-xl">
                      <div className="flex items-center gap-3">
                        <LocateFixed className="text-primary" size={16} />
                        <span className="text-xs font-bold text-primary">View Full Route Map</span>
                      </div>
                      <ChevronRight className="text-primary" size={16} />
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          ))}

          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-3"
            >
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <Cpu className="text-white" size={14} />
              </div>
              <div className="flex items-center gap-2 text-outline">
                <Loader2 size={16} className="animate-spin" />
                <span className="text-sm">FlowBot đang trả lời...</span>
              </div>
            </motion.div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Floating Input Bar */}
        <div className="fixed bottom-24 left-0 w-full px-4 flex justify-center z-40 pointer-events-none">
          <div className="w-full max-w-2xl bg-white/80 backdrop-blur-2xl rounded-2xl p-2 shadow-2xl border border-primary/10 flex items-center gap-2 pointer-events-auto">
            <button className="w-10 h-10 flex items-center justify-center text-outline hover:text-primary transition-colors">
              <Mic size={20} />
            </button>
            <input
              className="flex-1 bg-transparent border-none focus:ring-0 text-on-surface-variant font-sans text-base placeholder:text-outline/60 outline-hidden"
              placeholder="Bạn muốn đi đâu?"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="w-12 h-12 rounded-xl bg-linear-to-br from-primary to-primary-container text-white flex items-center justify-center active:scale-95 transition-transform disabled:opacity-50"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </main>
    </>
  );
}
