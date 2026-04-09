import { motion, AnimatePresence } from "motion/react";
import { Plus, MessageSquare, Trash2, X, Clock } from "lucide-react";
import { Conversation } from "../types";
import { cn } from "../lib/utils";

interface ConversationSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  conversations: Conversation[];
  activeId: string;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}

function formatRelativeTime(ts: number): string {
  const diff = Date.now() - ts;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Vừa xong";
  if (mins < 60) return `${mins} phút trước`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} giờ trước`;
  const days = Math.floor(hours / 24);
  return `${days} ngày trước`;
}

export default function ConversationSidebar({
  isOpen,
  onClose,
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
}: ConversationSidebarProps) {
  return (
    <>
      {/* Backdrop */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <AnimatePresence>
        {isOpen && (
          <motion.aside
            key="sidebar"
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "spring", damping: 28, stiffness: 300 }}
            className="fixed top-0 left-0 h-full w-80 max-w-[85vw] bg-white z-50 flex flex-col shadow-2xl"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-5 py-5 border-b border-surface-container-high">
              <div className="flex items-center gap-2">
                <MessageSquare className="text-primary" size={20} />
                <span className="font-headline font-bold text-lg text-primary">Lịch sử Chat</span>
              </div>
              <button
                onClick={onClose}
                className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors"
              >
                <X size={18} className="text-outline" />
              </button>
            </div>

            {/* New conversation button */}
            <div className="px-4 py-3 border-b border-surface-container-high">
              <button
                onClick={() => { onNew(); onClose(); }}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-primary text-white font-bold text-sm hover:bg-primary/90 active:scale-95 transition-all"
              >
                <Plus size={18} />
                Cuộc trò chuyện mới
              </button>
            </div>

            {/* Conversation list */}
            <div className="flex-1 overflow-y-auto py-2">
              {conversations.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full gap-3 text-outline">
                  <MessageSquare size={36} className="opacity-30" />
                  <p className="text-sm">Chưa có cuộc trò chuyện nào</p>
                </div>
              ) : (
                conversations.map((conv) => (
                  <div
                    key={conv.id}
                    className={cn(
                      "group flex items-start gap-3 px-4 py-3 mx-2 rounded-xl cursor-pointer transition-all",
                      conv.id === activeId
                        ? "bg-primary/10 border border-primary/20"
                        : "hover:bg-surface-container-low"
                    )}
                    onClick={() => { onSelect(conv.id); onClose(); }}
                  >
                    <div className="flex-1 min-w-0">
                      <p className={cn(
                        "text-sm font-semibold truncate",
                        conv.id === activeId ? "text-primary" : "text-on-surface"
                      )}>
                        {conv.title}
                      </p>
                      <div className="flex items-center gap-1 mt-1">
                        <Clock size={11} className="text-outline" />
                        <span className="text-xs text-outline">{formatRelativeTime(conv.updatedAt)}</span>
                        <span className="text-xs text-outline">· {conv.messages.length} tin</span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); onDelete(conv.id); }}
                      className="opacity-0 group-hover:opacity-100 w-7 h-7 flex items-center justify-center rounded-full hover:bg-error/10 transition-all flex-shrink-0 mt-0.5"
                    >
                      <Trash2 size={14} className="text-error" />
                    </button>
                  </div>
                ))
              )}
            </div>

            {/* Footer */}
            <div className="px-5 py-4 border-t border-surface-container-high">
              <p className="text-xs text-outline text-center">
                {conversations.length} cuộc trò chuyện · Lưu trên thiết bị
              </p>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}
