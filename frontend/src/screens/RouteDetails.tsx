import { motion } from "motion/react";
import { Video, MapPin, Navigation as NavIcon, Info, LocateFixed } from "lucide-react";
import { Stop } from "../types";
import { cn } from "../lib/utils";

export default function RouteDetails() {
  const stops: Stop[] = [
    { id: '1', name: 'Greenwich Village', time: 'Departed 14:02', status: 'past' },
    { id: '2', name: 'Station A', time: 'Arrived 14:15', status: 'current' },
    { id: '3', name: 'Station B', time: 'Arriving in 3 mins • 14:19', status: 'next' },
    { id: '4', name: 'North Harbour', time: 'Scheduled 14:24', status: 'future' },
    { id: '5', name: 'Central Station', time: 'Scheduled 14:32', status: 'future' }
  ];

  return (
    <main className="max-w-2xl mx-auto px-4 md:px-0 pb-32">
      {/* Map Canvas Section */}
      <section className="mt-4 relative overflow-hidden rounded-[2rem] h-[320px] bg-surface-container-low group shadow-lg">
        <img 
          className="w-full h-full object-cover" 
          src="https://picsum.photos/seed/route-map/800/400" 
          alt="Route Map"
          referrerPolicy="no-referrer"
        />
        {/* Glassmorphism Floating Card */}
        <div className="absolute bottom-6 left-6 right-6 p-5 bg-white/70 backdrop-blur-xl rounded-2xl border border-white/40 flex items-center justify-between shadow-xl">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-linear-to-br from-primary to-primary-container rounded-xl flex items-center justify-center text-white shadow-lg">
              <NavIcon size={24} />
            </div>
            <div>
              <p className="text-[10px] font-sans font-bold uppercase tracking-[0.1em] text-outline">Heading To</p>
              <h2 className="text-primary font-bold text-lg">Central Station</h2>
            </div>
          </div>
          <button className="bg-primary text-white px-5 py-3 rounded-xl font-headline font-bold text-sm flex items-center gap-2 active:scale-95 transition-all shadow-lg shadow-primary/20">
            <Video size={16} />
            Watch Live
          </button>
        </div>
      </section>

      {/* Dynamic Status Section */}
      <section className="mt-8 flex gap-4">
        <div className="flex-1 p-6 rounded-[2rem] bg-white border border-outline-variant/10 shadow-sm">
          <p className="text-[10px] font-sans font-bold uppercase tracking-[0.1em] text-outline mb-2">Current Stop</p>
          <div className="flex items-center gap-3">
            <MapPin className="text-primary" size={20} />
            <h3 className="font-headline font-bold text-xl text-primary">Station A</h3>
          </div>
        </div>
        <div className="flex-1 p-6 rounded-[2rem] bg-secondary-container/10 border border-secondary-container/20">
          <p className="text-[10px] font-sans font-bold uppercase tracking-[0.1em] text-secondary mb-2">Next Stop</p>
          <div className="flex items-center justify-between">
            <h3 className="font-headline font-bold text-xl text-on-secondary-container">Station B</h3>
            <div className="flex flex-col items-end">
              <span className="text-xs font-bold text-secondary">3 MINS</span>
              <div className="w-2 h-2 rounded-full bg-secondary animate-pulse mt-1"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Vertical Timeline Section */}
      <section className="mt-8">
        <div className="flex items-center justify-between px-2 mb-6">
          <h4 className="font-headline font-bold text-lg text-primary">Route Timeline</h4>
          <span className="text-xs font-medium text-outline">12 Stops Remaining</span>
        </div>
        <div className="relative space-y-0">
          {/* Timeline Line */}
          <div className="absolute left-[27px] top-4 bottom-4 w-[2px] bg-outline-variant/30"></div>
          
          {stops.map((stop, index) => (
            <motion.div 
              key={stop.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                "relative flex items-center gap-6 p-4 rounded-3xl transition-colors",
                stop.status === 'current' ? "bg-primary/5" : "hover:bg-surface-container-low/50"
              )}
            >
              <div className={cn(
                "z-10 flex items-center justify-center border-4 border-surface shadow-sm",
                stop.status === 'current' ? "w-10 h-10 -ml-2 rounded-full bg-primary" : "w-6 h-6 rounded-full bg-surface-container-highest"
              )}>
                {stop.status === 'current' ? (
                  <LocateFixed className="text-white" size={16} />
                ) : (
                  <div className={cn(
                    "w-2 h-2 rounded-full",
                    stop.status === 'past' ? "bg-outline" : stop.status === 'next' ? "bg-secondary" : "bg-outline-variant"
                  )} />
                )}
              </div>
              <div className={cn("flex-1", stop.status === 'past' && "opacity-50")}>
                <div className="flex items-center gap-2">
                  <h5 className={cn(
                    "font-headline font-bold text-lg",
                    stop.status === 'current' ? "text-primary font-extrabold" : "text-on-surface-variant"
                  )}>
                    {stop.name}
                  </h5>
                  {stop.status === 'current' && (
                    <span className="px-2 py-0.5 bg-primary text-[10px] text-white rounded-full font-bold uppercase tracking-widest">Now</span>
                  )}
                </div>
                <p className={cn(
                  "text-sm",
                  stop.status === 'next' ? "text-secondary font-semibold" : "text-outline"
                )}>
                  {stop.time}
                </p>
              </div>
              {stop.status === 'next' && <Info className="text-outline-variant" size={20} />}
            </motion.div>
          ))}
        </div>
      </section>
    </main>
  );
}
