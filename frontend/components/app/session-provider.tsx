'use client';

import { createContext, useContext, useMemo, useState } from 'react';
import { RoomContext } from '@livekit/components-react';
import { APP_CONFIG_DEFAULTS, type AppConfig } from '@/app-config';
import { useRoom } from '@/hooks/useRoom';

type ServiceType = 'chat' | 'coffee' | 'wellness' | null;

const SessionContext = createContext<{
  appConfig: AppConfig;
  isSessionActive: boolean;
  selectedService: ServiceType;
  setSelectedService: (service: ServiceType) => void;
  startSession: () => void;
  endSession: () => void;
}>({
  appConfig: APP_CONFIG_DEFAULTS,
  isSessionActive: false,
  selectedService: null,
  setSelectedService: () => { },
  startSession: () => { },
  endSession: () => { },
});

interface SessionProviderProps {
  appConfig: AppConfig;
  children: React.ReactNode;
}

export const SessionProvider = ({ appConfig, children }: SessionProviderProps) => {
  const [selectedService, setSelectedService] = useState<ServiceType>(null);
  const { room, isSessionActive, startSession, endSession } = useRoom(appConfig, selectedService);

  const contextValue = useMemo(
    () => ({ appConfig, isSessionActive, selectedService, setSelectedService, startSession, endSession }),
    [appConfig, isSessionActive, selectedService, startSession, endSession]
  );

  return (
    <RoomContext.Provider value={room}>
      <SessionContext.Provider value={contextValue}>{children}</SessionContext.Provider>
    </RoomContext.Provider>
  );
};

export function useSession() {
  return useContext(SessionContext);
}
