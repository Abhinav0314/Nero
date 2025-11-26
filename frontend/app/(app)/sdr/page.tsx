import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';

export const metadata = {
    title: 'SDR Assistant - Nero AI',
    description: 'Connect with Wipro sales representative',
};

export default async function SDRPage() {
    const hdrs = await headers();
    const appConfig = await getAppConfig(hdrs);

    return <App appConfig={appConfig} initialService="sdr" />;
}
