import { useState, useRef, useEffect } from "react";
import { motion } from "motion/react";
import { Send, Mic, Cpu, Radio, ChevronRight, LocateFixed, Loader2 } from "lucide-react";
import { Message, Route } from "../types";
import { cn } from "../lib/utils";

interface ChatProps {
  onSelectRoute: (routeId: string) => void;
}

interface ChatMessage extends Message {
  routes?: Route[];
}

export default function Chat({ onSelectRoute }: ChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      text: 'Xin chào! Tôi là FlowBot - trợ lý tìm tuyến bus VinBus. Bạn muốn đi đâu hôm nay?',
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });

      const data = await response.json();

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: data.reply || "Xin lỗi, tôi chưa hiểu ý bạn. Bạn có thể diễn đạt lại được không?",
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        routes: data.suggested_routes?.map((r: any, i: number) => ({
          id: r.bus_number || `route-${i}`,
          name: `BUS ${r.bus_number || '?'}`,
          eta: r.duration || 'N/A',
          gate: `${r.departure_stop} → ${r.arrival_stop}`,
          isLive: false,
        })),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: "Xin lỗi, tôi đang gặp sự cố kết nối. Bạn có thể thử lại được không?",
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <main className="max-w-4xl mx-auto px-4 pt-6 pb-32">
      <div className="space-y-8 pb-12">
        {messages.map((msg) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={cn(
              "flex flex-col space-y-2",
              msg.sender === 'user' ? "items-end" : "items-start"
            )}
          >
            {msg.sender === 'bot' && (
              <div className="flex items-center gap-3 mb-1">
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                  <Cpu className="text-white" size={14} />
                </div>
                <span className="font-headline font-bold text-sm tracking-tight text-primary">FlowBot</span>
              </div>
            )}
            <div className={cn(
              "max-w-[85%] md:max-w-[70%] px-6 py-4 shadow-sm",
              msg.sender === 'user' ? "chat-bubble-sender" : "chat-bubble-receiver"
            )}>
              <p className="text-[16px] leading-relaxed whitespace-pre-wrap">{msg.text}</p>
            </div>
            <span className="text-xs font-sans uppercase tracking-widest text-outline">
              {msg.sender === 'user' ? `Sent ${msg.timestamp}` : msg.timestamp}
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
                      <span className={cn(
                        "px-3 py-1 rounded-full text-[10px] font-black tracking-widest",
                        route.isLive ? "bg-secondary-container text-white" : "bg-surface-container-highest text-on-surface-variant"
                      )}>
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
          <button className="w-12 h-12 flex items-center justify-center text-outline hover:text-primary transition-colors">
            <Mic size={24} />
          </button>
          <input
            className="flex-1 bg-transparent border-none focus:ring-0 text-on-surface-variant font-sans text-base placeholder:text-outline/60 outline-hidden"
            placeholder="Where would you like to go?"
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
  );
}