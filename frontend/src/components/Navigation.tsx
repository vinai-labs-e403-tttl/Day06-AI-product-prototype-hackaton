import { motion } from "motion/react";
import { Bus, MessageSquare, Route, Map, Bookmark } from "lucide-react";
import { Screen } from "../types";
import { cn } from "../lib/utils";

interface NavigationProps {
  currentScreen: Screen;
  onNavigate: (screen: Screen) => void;
}

export default function Navigation({ currentScreen, onNavigate }: NavigationProps) {
  const tabs = [
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'route-details', label: 'Routes', icon: Route },
    { id: 'live-map', label: 'Live', icon: Map },
    { id: 'saved', label: 'Saved', icon: Bookmark },
  ];

  if (currentScreen === 'onboarding') return null;

  return (
    <nav className="fixed bottom-0 left-0 w-full flex justify-around items-center px-4 pb-6 pt-3 bg-white/80 backdrop-blur-xl z-50 rounded-t-[24px] shadow-[0_-8px_32px_rgba(0,64,161,0.06)] border-t border-primary/15">
      {tabs.map((tab) => {
        const isActive = currentScreen === tab.id || (tab.id === 'route-details' && currentScreen === 'route-details');
        const Icon = tab.icon;

        return (
          <button
            key={tab.id}
            onClick={() => onNavigate(tab.id as Screen)}
            className={cn(
              "flex flex-col items-center justify-center px-5 py-2 transition-all duration-200 active:scale-90",
              isActive 
                ? "bg-linear-to-br from-primary to-primary-container text-white rounded-2xl" 
                : "text-slate-500 hover:text-primary"
            )}
          >
            <Icon size={24} strokeWidth={isActive ? 2.5 : 2} />
            <span className="font-sans text-[10px] font-bold uppercase tracking-widest mt-1">
              {tab.label}
            </span>
          </button>
        );
      })}
    </nav>
  );
}
