import { motion } from "motion/react";
import { Bus, MessageSquare, MapPin, Train, Car } from "lucide-react";

interface OnboardingProps {
  onStart: () => void;
}

export default function Onboarding({ onStart }: OnboardingProps) {
  return (
    <main className="relative w-full max-w-screen-xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-12 lg:gap-24 py-12 md:py-24 overflow-hidden">
      {/* Left Column: Illustration & Visuals */}
      <div className="relative w-full md:w-1/2 flex justify-center items-center">
        {/* Decorative Blobs */}
        <div className="absolute -z-10 top-0 left-0 w-64 h-64 bg-primary-container/30 rounded-full blur-3xl"></div>
        <div className="absolute -z-10 bottom-0 right-0 w-80 h-80 bg-secondary-container/20 rounded-full blur-3xl"></div>
        
        {/* Main Illustration Container */}
        <div className="relative w-full aspect-square max-w-md">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="absolute inset-0 rounded-[48px] overflow-hidden shadow-2xl"
          >
            <img 
              className="w-full h-full object-cover" 
              src="https://picsum.photos/seed/transit-bus/800/800" 
              alt="Modern Transit"
              referrerPolicy="no-referrer"
            />
          </motion.div>

          {/* Floating Chatbot Interface */}
          <motion.div 
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="absolute -bottom-6 -right-6 md:-right-12 glass-panel p-6 rounded-3xl shadow-xl border border-white/40 max-w-[240px]"
          >
            <div className="flex items-center gap-4 mb-3">
              <div className="w-10 h-10 rounded-full bg-linear-to-br from-primary to-primary-container flex items-center justify-center shadow-lg">
                <MessageSquare className="text-white" size={20} />
              </div>
              <div>
                <p className="font-headline font-bold text-sm text-primary">TransitFlow Bot</p>
                <p className="text-[10px] text-primary/60 uppercase tracking-widest font-bold">Online Now</p>
              </div>
            </div>
            <div className="space-y-2">
              <div className="bg-surface-container-low p-2 rounded-xl rounded-tl-sm text-xs text-on-surface-variant">
                "Where do you want to go today?"
              </div>
              <div className="bg-primary/10 p-2 rounded-xl rounded-tr-sm text-xs text-primary self-end text-right">
                "Taking me to Central Station"
              </div>
            </div>
          </motion.div>

          {/* Live Pulse Indicator */}
          <div className="absolute top-8 left-8 flex items-center gap-2 bg-secondary-container px-4 py-2 rounded-full shadow-lg">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
            </span>
            <span className="text-[10px] font-bold uppercase tracking-wider text-white">Live Tracking</span>
          </div>
        </div>
      </div>

      {/* Right Column: Text & Actions */}
      <div className="w-full md:w-1/2 text-center md:text-left flex flex-col space-y-8">
        <header>
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-container-high mb-6"
          >
            <Bus className="text-primary" size={16} />
            <span className="text-xs font-bold font-sans uppercase tracking-widest text-primary">TransitFlow App</span>
          </motion.div>
          <motion.h1 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="font-headline font-extrabold text-5xl lg:text-7xl text-primary tracking-tighter leading-[1.1] mb-6"
          >
            Your Smart <br/>
            <span className="text-transparent bg-clip-text bg-linear-to-r from-primary via-primary-container to-secondary">Transit Companion</span>
          </motion.h1>
          <motion.p 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-on-surface-variant text-lg lg:text-xl max-w-lg mx-auto md:mx-0 leading-relaxed"
          >
            Find your way around the city using our AI chatbot. Just ask where you want to go!
          </motion.p>
        </header>

        <motion.div 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center gap-4 pt-4"
        >
          <button 
            onClick={onStart}
            className="w-full sm:w-auto px-10 py-5 bg-linear-to-br from-primary to-primary-container text-white font-headline font-bold text-lg rounded-xl shadow-2xl hover:scale-[1.02] active:scale-95 transition-all"
          >
            Get Started
          </button>
          <button className="w-full sm:w-auto px-10 py-5 bg-surface-container-low text-primary font-headline font-bold text-lg rounded-xl hover:bg-surface-container-high transition-colors">
            Learn More
          </button>
        </motion.div>

        {/* Social/Partners Proof */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="pt-12 border-t border-outline-variant/15"
        >
          <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-outline mb-6">Trusted by commuters in</p>
          <div className="flex flex-wrap justify-center md:justify-start gap-8 opacity-60 grayscale">
            <div className="flex items-center gap-2">
              <MapPin size={20} />
              <span className="font-headline font-bold">METROPOLIS</span>
            </div>
            <div className="flex items-center gap-2">
              <Train size={20} />
              <span className="font-headline font-bold">URBANRAIL</span>
            </div>
            <div className="flex items-center gap-2">
              <Car size={20} />
              <span className="font-headline font-bold">CITYLINE</span>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
