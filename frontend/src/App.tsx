import { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Screen } from './types';
import Header from './components/Header';
import Navigation from './components/Navigation';
import Onboarding from './screens/Onboarding';
import Chat from './screens/Chat';
import RouteDetails from './screens/RouteDetails';
import LiveMap from './screens/LiveMap';

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('onboarding');

  const renderScreen = () => {
    switch (currentScreen) {
      case 'onboarding':
        return <Onboarding onStart={() => setCurrentScreen('chat')} />;
      case 'chat':
        return <Chat onSelectRoute={() => setCurrentScreen('route-details')} />;
      case 'route-details':
        return <RouteDetails />;
      case 'live-map':
        return <LiveMap />;
      default:
        return <Onboarding onStart={() => setCurrentScreen('chat')} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header 
        currentScreen={currentScreen} 
        onBack={currentScreen !== 'onboarding' ? () => setCurrentScreen('chat') : undefined} 
      />
      
      <div className="flex-1 relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentScreen}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="w-full h-full"
          >
            {renderScreen()}
          </motion.div>
        </AnimatePresence>
      </div>

      <Navigation 
        currentScreen={currentScreen} 
        onNavigate={setCurrentScreen} 
      />

      {/* Footer Decorative Elements */}
      <div className="fixed bottom-0 left-0 w-full h-1 bg-linear-to-r from-primary via-secondary to-primary-container z-50"></div>
    </div>
  );
}
