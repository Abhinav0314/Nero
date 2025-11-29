import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';

export const metadata = {
  title: 'General Chat - Nero AI',
  description: 'Chat with your AI assistant',
};

export default async function ChatPage() {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);

  return <App appConfig={appConfig} initialService="chat" />;
}
