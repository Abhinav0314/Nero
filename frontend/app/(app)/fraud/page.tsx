import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';

export const metadata = {
    title: 'Fraud Alert - Nero AI',
    description: 'Verify suspicious transactions with SecureBank',
};

export default async function FraudPage() {
    const hdrs = await headers();
    const appConfig = await getAppConfig(hdrs);

    return <App appConfig={appConfig} initialService="fraud" />;
}
