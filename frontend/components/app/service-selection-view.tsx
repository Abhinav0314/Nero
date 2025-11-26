import Link from 'next/link';
import { Button } from '@/components/livekit/button';

function ServiceIcon({ type }: { type: 'chat' | 'coffee' | 'wellness' | 'tutor' | 'sdr' | 'fraud' }) {
    if (type === 'chat') {
        return (
            <svg
                width="48"
                height="48"
                viewBox="0 0 64 64"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="text-fg0 mb-3 size-12"
            >
                <path
                    d="M32 8C18.7452 8 8 17.9086 8 30C8 35.4903 10.0645 40.5161 13.4839 44.4839L10.0645 54.0645C9.80645 54.8387 10.0645 55.6774 10.6452 56.1935C11.0323 56.5161 11.4839 56.6774 11.9355 56.6774C12.2581 56.6774 12.5806 56.5806 12.8387 56.4516L24.5161 50.5806C27.0323 51.2903 29.4839 51.6774 32 51.6774C45.2548 51.6774 56 41.7688 56 30C56 17.9086 45.2548 8 32 8ZM32 46C29.8065 46 27.6129 45.6774 25.4839 45.0323L24.3871 44.7097L16.5161 48.3871L18.8387 41.3548L18.0645 40.3871C14.9677 36.7742 13.2258 32.4516 13.2258 28C13.2258 20.7097 21.8065 13.2258 32 13.2258C42.1935 13.2258 50.7742 20.7097 50.7742 28C50.7742 35.2903 42.1935 46 32 46Z"
                    fill="currentColor"
                />
            </svg>
        );
    }

    if (type === 'coffee') {
        return (
            <svg
                width="48"
                height="48"
                viewBox="0 0 64 64"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="text-fg0 mb-3 size-12"
            >
                <path
                    d="M52 16H48V12C48 10.9391 47.5786 9.92172 46.8284 9.17157C46.0783 8.42143 45.0609 8 44 8H12C10.9391 8 9.92172 8.42143 9.17157 9.17157C8.42143 9.92172 8 10.9391 8 12V40C8 43.1826 9.26428 46.2348 11.5147 48.4853C13.7652 50.7357 16.8174 52 20 52H36C39.1826 52 42.2348 50.7357 44.4853 48.4853C46.7357 46.2348 48 43.1826 48 40V28H52C53.0609 28 54.0783 27.5786 54.8284 26.8284C55.5786 26.0783 56 25.0609 56 24V20C56 18.9391 55.5786 17.9217 54.8284 17.1716C54.0783 16.4214 53.0609 16 52 16ZM48 24V20H52V24H48ZM12 12H44V40C44 42.1217 43.1571 44.1566 41.6569 45.6569C40.1566 47.1571 38.1217 48 36 48H20C17.8783 48 15.8434 47.1571 14.3431 45.6569C12.8429 44.1566 12 42.1217 12 40V12Z"
                    fill="currentColor"
                />
            </svg>
        );
    }

    if (type === 'wellness') {
        return (
            <svg
                width="48"
                height="48"
                viewBox="0 0 64 64"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="text-fg0 mb-3 size-12"
            >
                <path
                    d="M32 56C30.9 56 30 55.1 30 54V10C30 8.9 30.9 8 32 8C33.1 8 34 8.9 34 10V54C34 55.1 33.1 56 32 56ZM44 44C42.9 44 42 43.1 42 42V22C42 20.9 42.9 20 44 20C45.1 20 46 20.9 46 22V42C46 43.1 45.1 44 44 44ZM20 44C18.9 44 18 43.1 18 42V22C18 20.9 18.9 20 20 20C21.1 20 22 20.9 22 22V42C22 43.1 21.1 44 20 44ZM56 36C54.9 36 54 35.1 54 34V30C54 28.9 54.9 28 56 28C57.1 28 58 28.9 58 30V34C58 35.1 57.1 36 56 36ZM8 36C6.9 36 6 35.1 6 34V30C6 28.9 6.9 28 8 28C9.1 28 10 28.9 10 30V34C10 35.1 9.1 36 8 36Z"
                    fill="currentColor"
                />
            </svg>
        );
    }

    // tutor
    if (type === 'tutor') {
        return (
            <svg
                width="48"
                height="48"
                viewBox="0 0 64 64"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="text-fg0 mb-3 size-12"
            >
                <path
                    d="M16 12C13.7909 12 12 13.7909 12 16V48C12 50.2091 13.7909 52 16 52H48C50.2091 52 52 50.2091 52 48V16C52 13.7909 50.2091 12 48 12H16ZM48 16V48H16V16H48ZM20 20H44V24H20V20ZM20 28H44V32H20V28ZM20 36H36V40H20V36Z"
                    fill="currentColor"
                />
            </svg>
        );
    }

    // sdr
    if (type === 'sdr') {
        return (
            <svg
                width="48"
                height="48"
                viewBox="0 0 64 64"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="text-fg0 mb-3 size-12"
            >
                <path
                    d="M52 20H48V16C48 14.9391 47.5786 13.9217 46.8284 13.1716C46.0783 12.4214 45.0609 12 44 12H20C18.9391 12 17.9217 12.4214 17.1716 13.1716C16.4214 13.9217 16 14.9391 16 16V20H12C10.9391 20 9.92172 20.4214 9.17157 21.1716C8.42143 21.9217 8 22.9391 8 24V28C8 29.0609 8.42143 30.0783 9.17157 30.8284C9.92172 31.5786 10.9391 32 12 32H16V48C16 49.0609 16.4214 50.0783 17.1716 50.8284C17.9217 51.5786 18.9391 52 20 52H44C45.0609 52 46.0783 51.5786 46.8284 50.8284C47.5786 50.0783 48 49.0609 48 48V32H52C53.0609 32 54.0783 31.5786 54.8284 30.8284C55.5786 30.0783 56 29.0609 56 28V24C56 22.9391 55.5786 21.9217 54.8284 21.1716C54.0783 20.4214 53.0609 20 52 20ZM12 28V24H16V28H12ZM44 48H20V16H44V48ZM52 28H48V24H52V28ZM28 24H36V28H28V24ZM24 36H40V40H24V36Z"
                    fill="currentColor"
                />
            </svg>
        );
    }


}

interface ServiceSelectionViewProps {
    onSelectService?: (service: 'chat' | 'coffee' | 'wellness' | 'tutor' | 'sdr' | 'fraud') => void;
}

export const ServiceSelectionView = ({
    onSelectService,
    ref,
}: React.ComponentProps<'div'> & ServiceSelectionViewProps) => {
    return (
        <div ref={ref}>
            <section className="bg-background flex flex-col items-center justify-center text-center px-4">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-foreground text-3xl md:text-4xl font-bold mb-2">
                        Welcome to Nero AI Services
                    </h1>
                    <p className="text-muted-foreground text-base md:text-lg">
                        Choose a service to get started
                    </p>
                </div>

                {/* Service Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl w-full">
                    {/* General Chat */}
                    <Link
                        href="/chat"
                        className="bg-card hover:bg-accent/10 border border-border rounded-lg p-6 transition-all duration-200 hover:scale-105 hover:shadow-lg text-center group block"
                    >
                        <div className="flex flex-col items-center">
                            <ServiceIcon type="chat" />
                            <h3 className="text-foreground text-xl font-semibold mb-2">
                                General Chat
                            </h3>
                            <p className="text-muted-foreground text-sm leading-relaxed">
                                Have a friendly conversation about anything
                            </p>
                        </div>
                    </Link>

                    {/* Coffee Order */}
                    <Link
                        href="/coffee"
                        className="bg-card hover:bg-accent/10 border border-border rounded-lg p-6 transition-all duration-200 hover:scale-105 hover:shadow-lg text-center group block"
                    >
                        <div className="flex flex-col items-center">
                            <ServiceIcon type="coffee" />
                            <h3 className="text-foreground text-xl font-semibold mb-2">
                                Coffee Ordering
                            </h3>
                            <p className="text-muted-foreground text-sm leading-relaxed">
                                Place an order at our virtual coffee shop
                            </p>
                        </div>
                    </Link>

                    {/* Wellness Check-in */}
                    <Link
                        href="/wellness"
                        className="bg-card hover:bg-accent/10 border border-border rounded-lg p-6 transition-all duration-200 hover:scale-105 hover:shadow-lg text-center group block"
                    >
                        <div className="flex flex-col items-center">
                            <ServiceIcon type="wellness" />
                            <h3 className="text-foreground text-xl font-semibold mb-2">
                                Wellness Check-in
                            </h3>
                            <p className="text-muted-foreground text-sm leading-relaxed">
                                Daily reflection on mood, energy, and goals
                            </p>
                        </div>
                    </Link>

                    {/* Tutor */}
                    <Link
                        href="/tutor"
                        className="bg-card hover:bg-accent/10 border border-border rounded-lg p-6 transition-all duration-200 hover:scale-105 hover:shadow-lg text-center group block"
                    >
                        <div className="flex flex-col items-center">
                            <ServiceIcon type="tutor" />
                            <h3 className="text-foreground text-xl font-semibold mb-2">
                                Active Recall Tutor
                            </h3>
                            <p className="text-muted-foreground text-sm leading-relaxed">
                                Learn concepts through teaching and quizzes
                            </p>
                        </div>
                    </Link>

                    {/* SDR Assistant */}
                    <Link
                        href="/sdr"
                        className="bg-card hover:bg-accent/10 border border-border rounded-lg p-6 transition-all duration-200 hover:scale-105 hover:shadow-lg text-center group block"
                    >
                        <div className="flex flex-col items-center">
                            <ServiceIcon type="sdr" />
                            <h3 className="text-foreground text-xl font-semibold mb-2">
                                SDR Assistant
                            </h3>
                            <p className="text-muted-foreground text-sm leading-relaxed">
                                Learn about Wipro services and solutions
                            </p>
                        </div>
                    </Link>


                </div>
            </section>

            <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
                <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm">
                    Powered by Murf Falcon TTS, LiveKit, and Google Gemini
                </p>
            </div>
        </div>
    );
};
