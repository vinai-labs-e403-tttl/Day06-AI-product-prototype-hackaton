export type Screen = 'onboarding' | 'chat' | 'route-details' | 'live-map';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: string;
}

export interface Route {
  id: string;
  name: string;
  eta: string;
  gate: string;
  isLive?: boolean;
}

export interface Stop {
  id: string;
  name: string;
  time: string;
  status: 'past' | 'current' | 'next' | 'future';
}
