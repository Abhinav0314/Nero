import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Room, RoomEvent, TokenSource } from 'livekit-client';
import { AppConfig } from '@/app-config';
import { toastAlert } from '@/components/livekit/alert-toast';

type ServiceType = 'chat' | 'coffee' | 'wellness' | 'tutor' | null;

export function useRoom(appConfig: AppConfig, selectedService: ServiceType) {
  const aborted = useRef(false);
  const room = useMemo(() => new Room(), []);
  const [isSessionActive, setIsSessionActive] = useState(false);

  useEffect(() => {
    function onDisconnected() {
      setIsSessionActive(false);
    }

    function onMediaDevicesError(error: Error) {
      toastAlert({
        title: 'Encountered an error with your media devices',
        description: `${error.name}: ${error.message}`,
      });
    }

    room.on(RoomEvent.Disconnected, onDisconnected);
    room.on(RoomEvent.MediaDevicesError, onMediaDevicesError);

    return () => {
      room.off(RoomEvent.Disconnected, onDisconnected);
      room.off(RoomEvent.MediaDevicesError, onMediaDevicesError);
    };
  }, [room]);

  useEffect(() => {
    return () => {
      aborted.current = true;
      room.disconnect();
    };
  }, [room]);

  const tokenSource = useMemo(
    () =>
      TokenSource.custom(async () => {
        const url = new URL(
          process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT ?? '/api/connection-details',
          window.location.origin
        );

        const requestBody = {
          room_config: appConfig.agentName
            ? {
              agents: [{ agent_name: appConfig.agentName }],
            }
            : undefined,
          metadata: {
            service: selectedService,
          },
        };

        console.log('[useRoom] Fetching connection details for service:', selectedService);
        console.log('[useRoom] Request body:', JSON.stringify(requestBody, null, 2));

        try {
          const res = await fetch(url.toString(), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Sandbox-Id': appConfig.sandboxId ?? '',
            },
            body: JSON.stringify(requestBody),
          });

          if (!res.ok) {
            const errorText = await res.text();
            console.error('[useRoom] Failed to fetch connection details:', res.status, errorText);
            throw new Error(`Failed to fetch connection details: ${res.status} ${res.statusText}`);
          }

          const connectionDetails = await res.json();
          console.log('[useRoom] ✓ Connection details received successfully');
          return connectionDetails;
        } catch (error) {
          console.error('[useRoom] Error fetching connection details:', error);
          throw new Error(`Error fetching connection details: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      }),
    [appConfig, selectedService]
  );

  const startSession = useCallback(() => {
    console.log('[useRoom] Starting session for service:', selectedService);
    setIsSessionActive(true);

    if (room.state === 'disconnected') {
      const { isPreConnectBufferEnabled } = appConfig;
      console.log('[useRoom] Room is disconnected, initiating connection...');
      console.log('[useRoom] PreConnect buffer enabled:', isPreConnectBufferEnabled);

      Promise.all([
        room.localParticipant.setMicrophoneEnabled(true, undefined, {
          preConnectBuffer: isPreConnectBufferEnabled,
        }),
        tokenSource
          .fetch({ agentName: appConfig.agentName })
          .then((connectionDetails) => {
            console.log('[useRoom] ✓ Connecting to room with token...');
            return room.connect(connectionDetails.serverUrl, connectionDetails.participantToken);
          }),
      ])
        .then(() => {
          console.log('[useRoom] ✓ Successfully connected to room');
        })
        .catch((error) => {
          if (aborted.current) {
            // Once the effect has cleaned up after itself, drop any errors
            //
            // These errors are likely caused by this effect rerunning rapidly,
            // resulting in a previous run `disconnect` running in parallel with
            // a current run `connect`
            console.log('[useRoom] Connection aborted (cleanup in progress)');
            return;
          }

          console.error('[useRoom] Connection error:', error);
          toastAlert({
            title: 'There was an error connecting to the agent',
            description: `${error.name}: ${error.message}`,
          });
        });
    } else {
      console.log('[useRoom] Room already connected, state:', room.state);
    }
  }, [room, appConfig, tokenSource, selectedService]);

  const endSession = useCallback(() => {
    setIsSessionActive(false);
  }, []);

  return { room, isSessionActive, startSession, endSession };
}
