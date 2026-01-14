import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'Multi-Agent RAG | Intelligent Knowledge Assistant',
    description: 'Production-ready conversational AI with 8-agent hierarchical orchestration and 90%+ retrieval precision',
    keywords: ['RAG', 'AI', 'LangGraph', 'LangChain', 'Multi-Agent'],
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <head>
                <link rel="icon" href="/favicon.ico" />
                <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
            </head>
            <body className="min-h-screen font-sans antialiased">
                <div className="relative min-h-screen">
                    {/* Background gradient */}
                    <div className="fixed inset-0 -z-10 overflow-hidden">
                        <div className="absolute -top-[40%] -right-[20%] w-[80%] h-[80%] rounded-full bg-gradient-to-br from-primary-500/5 via-accent-500/5 to-transparent blur-3xl" />
                        <div className="absolute -bottom-[40%] -left-[20%] w-[80%] h-[80%] rounded-full bg-gradient-to-tr from-accent-500/5 via-primary-500/5 to-transparent blur-3xl" />
                    </div>

                    {children}
                </div>
            </body>
        </html>
    );
}
