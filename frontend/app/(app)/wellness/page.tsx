import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';

export const metadata = {
    title: 'Wellness Check-in - Nero AI',
    description: 'Daily wellness and mindfulness check-in',
};

export default async function WellnessPage() {
    const hdrs = await headers();
    const appConfig = await getAppConfig(hdrs);

    return <App appConfig={appConfig} initialService="wellness" />;
}
