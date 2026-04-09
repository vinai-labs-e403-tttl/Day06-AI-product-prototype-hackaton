import { motion } from "motion/react";
import { Bus, MapPin, Navigation, Layers, LocateFixed, Bell } from "lucide-react";

export default function LiveMap() {
  return (
    <main className="relative h-[calc(100vh-144px)] md:h-[calc(100vh-76px)] overflow-hidden">
      {/* Map Canvas */}
      <div className="absolute inset-0 z-0 bg-surface-container-low">
        <img 
          className="w-full h-full object-cover opacity-60 grayscale" 
          src="https://picsum.photos/seed/full-map/1200/800" 
          alt="Map"
          referrerPolicy="no-referrer"
        />
        
        {/* Overlay for Tonal Depth */}
        <div className="absolute inset-0 bg-primary/5"></div>

        {/* Route Path (SVG Overlay Simulation) */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
          <path 
            d="M-100,200 Q200,150 400,400 T800,300 T1200,600" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="6" 
            className="text-primary/20"
          />
          <path 
            d="M-100,200 Q200,150 400,400 T800,300 T1200,600" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="3" 
            strokeDasharray="8 8" 
            className="text-primary/40"
          />
        </svg>

        {/* Current Location Indicator */}
        <div className="absolute top-1/2 left-1/3 -translate-x-1/2 -translate-y-1/2">
          <div className="relative flex items-center justify-center">
            <div className="absolute w-12 h-12 bg-primary/20 rounded-full animate-ping"></div>
            <div className="w-6 h-6 bg-primary border-4 border-white rounded-full shadow-2xl"></div>
          </div>
        </div>

        {/* Live Bus Icon */}
        <motion.div 
          initial={{ x: 100, y: 100 }}
          animate={{ x: 0, y: 0 }}
          transition={{ duration: 10, repeat: Infinity, repeatType: "reverse" }}
          className="absolute top-[40%] left-[60%] -translate-x-1/2 -translate-y-1/2 group cursor-pointer"
        >
          <div className="relative">
            {/* Glow Pulse */}
            <div className="absolute inset-0 w-16 h-16 -translate-x-1/4 -translate-y-1/4 bg-secondary/20 rounded-full blur-xl"></div>
            {/* Bus Pin */}
            <div className="relative bg-linear-to-br from-primary to-primary-container p-3 rounded-2xl shadow-2xl flex items-center justify-center border-2 border-white/20 active:scale-95 transition-transform">
              <Bus className="text-white" size={24} />
              <div className="absolute -top-1 -right-1 bg-secondary-container text-white px-2 py-0.5 rounded-full text-[10px] font-bold tracking-tighter">42</div>
            </div>
            {/* Tooltip Style Label */}
            <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-lg shadow-lg border border-outline-variant/15 whitespace-nowrap">
              <span className="text-xs font-bold font-sans uppercase tracking-widest text-primary">Moving Now</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Floating Action Map Controls */}
      <div className="absolute top-6 right-6 flex flex-col gap-3">
        <button className="w-12 h-12 bg-white/80 backdrop-blur-md rounded-xl shadow-xl flex items-center justify-center text-on-surface-variant hover:bg-white transition-colors">
          <LocateFixed size={24} />
        </button>
        <button className="w-12 h-12 bg-white/80 backdrop-blur-md rounded-xl shadow-xl flex items-center justify-center text-on-surface-variant hover:bg-white transition-colors">
          <Layers size={24} />
        </button>
      </div>

      {/* Kinetic Floating Card (Bottom) */}
      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 w-[90%] max-w-lg z-10">
        <motion.div 
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="bg-white/85 backdrop-blur-2xl rounded-[32px] p-6 shadow-2xl border border-white/40"
        >
          {/* Header Info */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex gap-4">
              <div className="w-14 h-14 bg-secondary-container rounded-2xl flex flex-col items-center justify-center text-white shadow-lg">
                <span className="text-[10px] font-bold opacity-80">BUS</span>
                <span className="text-2xl font-extrabold leading-tight">42</span>
              </div>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="font-headline font-bold text-xl text-primary">Route 42</h2>
                  <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider">On Time</span>
                </div>
                <p className="text-on-surface-variant font-medium flex items-center gap-1">
                  <MapPin size={14} />
                  Toward West Central Station
                </p>
              </div>
            </div>
          </div>

          {/* Live Stats Bento-ish Row */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-surface-container-low p-4 rounded-2xl border border-outline-variant/10">
              <span className="text-[10px] font-bold font-sans text-outline uppercase tracking-widest block mb-1">Distance</span>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-bold font-headline text-primary">1.2</span>
                <span className="text-sm font-bold text-on-surface-variant uppercase">km</span>
              </div>
            </div>
            <div className="bg-primary/5 p-4 rounded-2xl border border-primary/10">
              <span className="text-[10px] font-bold font-sans text-primary uppercase tracking-widest block mb-1">Estimated Arrival</span>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-bold font-headline text-primary">4</span>
                <span className="text-sm font-bold text-primary uppercase">mins</span>
              </div>
            </div>
          </div>

          {/* Call to Action */}
          <button className="w-full bg-linear-to-br from-primary to-primary-container text-white py-4 px-6 rounded-2xl font-headline font-bold text-base flex items-center justify-center gap-2 shadow-xl hover:scale-[1.02] active:scale-95 transition-all">
            <Bell size={20} />
            Notify Me
          </button>
        </motion.div>
      </div>
    </main>
  );
}
