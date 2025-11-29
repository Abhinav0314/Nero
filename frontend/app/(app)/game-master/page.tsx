import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';

export const metadata = {
  title: 'D&D Game Master - Nero AI',
  description: 'Embark on a voice-based D&D adventure with AI Game Master',
};

export default async function GameMasterPage() {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);

  return <App appConfig={appConfig} initialService="game-master" />;
}
