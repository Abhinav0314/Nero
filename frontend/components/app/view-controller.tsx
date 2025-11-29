'use client';

import { useRef } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { useRoomContext } from '@livekit/components-react';
import { ServiceSelectionView } from '@/components/app/service-selection-view';
import { useSession } from '@/components/app/session-provider';
import { SessionView } from '@/components/app/session-view';
import { WelcomeView } from '@/components/app/welcome-view';

const MotionServiceSelectionView = motion.create(ServiceSelectionView);
const MotionWelcomeView = motion.create(WelcomeView);
const MotionSessionView = motion.create(SessionView);

const VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
    },
    hidden: {
      opacity: 0,
    },
  },
  initial: 'hidden' as const,
  animate: 'visible' as const,
  exit: 'hidden' as const,
  transition: {
    duration: 0.5,
  },
} as const;

const SERVICE_LABELS = {
  chat: 'Start chatting',
  coffee: 'Start ordering',
  wellness: 'Start check-in',
  tutor: 'Start learning',
  sdr: 'Start conversation',
  fraud: 'Start verification',
  grocery: 'Start shopping',
  'game-master': 'Start adventure',
};

export function ViewController() {
  const room = useRoomContext();
  const isSessionActiveRef = useRef(false);
  const { appConfig, isSessionActive, selectedService, setSelectedService, startSession } =
    useSession();

  // animation handler holds a reference to stale isSessionActive value
  isSessionActiveRef.current = isSessionActive;

  // disconnect room after animation completes
  const handleAnimationComplete = () => {
    if (!isSessionActiveRef.current && room.state !== 'disconnected') {
      room.disconnect();
    }
  };

  const handleServiceSelection = (
    service: 'chat' | 'coffee' | 'wellness' | 'tutor' | 'sdr' | 'fraud' | 'grocery' | 'game-master'
  ) => {
    setSelectedService(service);
  };

  const startButtonText = selectedService
    ? SERVICE_LABELS[selectedService]
    : appConfig.startButtonText;

  return (
    <AnimatePresence mode="wait">
      {/* Service selection screen */}
      {!selectedService && !isSessionActive && (
        <MotionServiceSelectionView
          key="service-selection"
          {...VIEW_MOTION_PROPS}
          onSelectService={handleServiceSelection}
        />
      )}
      {/* Welcome screen */}
      {selectedService && !isSessionActive && (
        <MotionWelcomeView
          key="welcome"
          {...VIEW_MOTION_PROPS}
          startButtonText={startButtonText}
          onStartCall={startSession}
        />
      )}
      {/* Session view */}
      {isSessionActive && (
        <MotionSessionView
          key="session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
          onAnimationComplete={handleAnimationComplete}
        />
      )}
    </AnimatePresence>
  );
}
