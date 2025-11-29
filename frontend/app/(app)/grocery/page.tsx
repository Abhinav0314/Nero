import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';

export const metadata = {
  title: 'Grocery Ordering - Nero AI',
  description: 'Order fresh groceries and prepared foods from FreshMart',
};

export default async function GroceryPage() {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);

  return <App appConfig={appConfig} initialService="grocery" />;
}
