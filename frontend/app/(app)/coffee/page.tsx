import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';

export const metadata = {
  title: 'Coffee Shop - Nero AI',
  description: 'Order your favorite coffee',
};

export default async function CoffeePage() {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);

  return <App appConfig={appConfig} initialService="coffee" />;
}
