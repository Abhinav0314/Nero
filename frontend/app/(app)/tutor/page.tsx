import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';

export const metadata = {
    title: 'Active Recall Tutor - Nero AI',
    description: 'Learn programming concepts through active recall',
};

export default async function TutorPage() {
    const hdrs = await headers();
    const appConfig = await getAppConfig(hdrs);

    return <App appConfig={appConfig} initialService="tutor" />;
}
