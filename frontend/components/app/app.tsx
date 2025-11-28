'use client';

import { RoomAudioRenderer, StartAudio } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { SessionProvider } from '@/components/app/session-provider';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/livekit/toaster';

interface AppProps {
  appConfig: AppConfig;
  initialService?: 'chat' | 'coffee' | 'wellness' | 'tutor' | 'sdr' | 'fraud' | 'grocery';
}

export function App({ appConfig, initialService }: AppProps) {
  return (
    <SessionProvider appConfig={appConfig} initialService={initialService}>
      <main className="grid h-svh grid-cols-1 place-content-center">
        <ViewController />
      </main>
      <StartAudio label="Start Audio" />
      <RoomAudioRenderer />
      <Toaster />
    </SessionProvider>
  );
}
