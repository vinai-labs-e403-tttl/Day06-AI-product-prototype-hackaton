import { Bus, Languages } from "lucide-react";
import { Screen } from "../types";

interface HeaderProps {
  currentScreen: Screen;
  onBack?: () => void;
}

export default function Header({ currentScreen, onBack }: HeaderProps) {
  if (currentScreen === 'onboarding') {
    return (
      <nav className="fixed top-0 left-0 w-full z-50 px-6 py-6 flex justify-between items-center glass-panel">
        <div className="flex items-center gap-2">
          <Bus className="text-primary italic" size={32} />
          <span className="font-headline font-extrabold text-2xl tracking-tight text-primary italic">TransitFlow</span>
        </div>
        <div className="hidden md:flex items-center gap-8">
          <a className="text-sm font-bold font-sans uppercase tracking-widest text-on-surface-variant hover:text-primary transition-colors" href="#">Routes</a>
          <a className="text-sm font-bold font-sans uppercase tracking-widest text-on-surface-variant hover:text-primary transition-colors" href="#">Live Map</a>
          <a className="text-sm font-bold font-sans uppercase tracking-widest text-on-surface-variant hover:text-primary transition-colors" href="#">Support</a>
        </div>
        <button className="p-2 rounded-full bg-surface-container-low hover:bg-surface-container-high transition-colors">
          <Languages className="text-on-surface-variant" size={20} />
        </button>
      </nav>
    );
  }

  const titles: Record<Screen, string> = {
    'onboarding': '',
    'chat': 'Navigator',
    'route-details': 'Route 42',
    'live-map': 'Navigator'
  };

  return (
    <header className="w-full top-0 sticky bg-surface-container-low z-50">
      <div className="flex items-center justify-between px-6 py-4 w-full">
        <div className="flex items-center gap-3">
          {onBack && (
            <button onClick={onBack} className="md:hidden">
              <Bus className="text-primary" size={24} />
            </button>
          )}
          {!onBack && <Bus className="text-primary" size={24} />}
          <h1 className="font-headline font-bold text-2xl tracking-tight text-primary italic">
            {titles[currentScreen]}
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-primary-container bg-surface-container-highest">
            <img 
              className="w-full h-full object-cover" 
              src="https://picsum.photos/seed/user123/100/100" 
              alt="User"
              referrerPolicy="no-referrer"
            />
          </div>
        </div>
      </div>
    </header>
  );
}
