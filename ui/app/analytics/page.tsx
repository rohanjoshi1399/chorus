'use client';

import Link from 'next/link';
import {
    ArrowLeft,
    BarChart3,
    TrendingUp,
    Clock,
    Target,
    CheckCircle,
    HelpCircle,
    ArrowUpRight,
} from 'lucide-react';

export default function AnalyticsPage() {
    return (
        <div className="min-h-screen">
            {/* Header */}
            <header className="glass border-b border-surface-200/50 dark:border-surface-700/50 sticky top-0 z-40">
                <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="btn-ghost p-2" title="Back to home">
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                                <BarChart3 className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h1 className="text-h4 font-semibold">Performance</h1>
                                <p className="text-caption text-surface-500 hidden sm:block">
                                    How well the AI is working
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 py-8">
                {/* Explanation */}
                <div className="mb-8 p-4 rounded-xl bg-primary-500/5 border border-primary-200/50 dark:border-primary-800/50">
                    <div className="flex items-start gap-3">
                        <HelpCircle className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-body-sm text-surface-700 dark:text-surface-300">
                                <strong>What do these numbers mean?</strong> These metrics show how accurately and quickly
                                the AI finds and presents information from your documents. Higher percentages mean better
                                performance.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Key Metrics - simplified labels */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    <MetricCard
                        icon={Target}
                        label="Answer Accuracy"
                        value="92%"
                        subtext="9 out of 10 answers are spot-on"
                        isGood={true}
                    />
                    <MetricCard
                        icon={CheckCircle}
                        label="Source Quality"
                        value="96%"
                        subtext="Answers backed by real sources"
                        isGood={true}
                    />
                    <MetricCard
                        icon={TrendingUp}
                        label="Relevance"
                        value="91%"
                        subtext="Finds the right information"
                        isGood={true}
                    />
                    <MetricCard
                        icon={Clock}
                        label="Speed"
                        value="1.2s"
                        subtext="Average response time"
                        isGood={true}
                    />
                </div>

                {/* Charts Section */}
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                    {/* Usage Over Time */}
                    <div className="card p-6">
                        <h3 className="text-h4 mb-1">Questions Asked Today</h3>
                        <p className="text-caption text-surface-500 mb-4">How many questions you've asked</p>
                        <div className="h-40 flex items-end gap-2">
                            {mockQueryData.map((value, i) => (
                                <div key={i} className="flex-1 flex flex-col items-center gap-2">
                                    <div
                                        className="w-full bg-gradient-to-t from-primary-500 to-primary-400 rounded-t transition-all hover:from-primary-600 hover:to-primary-500 cursor-pointer"
                                        style={{ height: `${(value / 100) * 100}%` }}
                                        title={`${value} questions`}
                                    />
                                    <span className="text-caption text-surface-400">{i * 3}h</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Search Methods Used */}
                    <div className="card p-6">
                        <h3 className="text-h4 mb-1">How Answers Are Found</h3>
                        <p className="text-caption text-surface-500 mb-4">Methods used to find information</p>
                        <div className="space-y-4">
                            {strategies.map((strategy) => (
                                <div key={strategy.name}>
                                    <div className="flex justify-between text-body-sm mb-1">
                                        <span>{strategy.name}</span>
                                        <span className="text-surface-500">{strategy.percentage}%</span>
                                    </div>
                                    <div className="h-3 bg-surface-100 dark:bg-surface-800 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full rounded-full transition-all ${strategy.color}`}
                                            style={{ width: `${strategy.percentage}%` }}
                                        />
                                    </div>
                                    <p className="text-caption text-surface-400 mt-1">{strategy.description}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Simple Metrics Table */}
                <div className="card overflow-hidden">
                    <div className="p-4 border-b border-surface-200 dark:border-surface-700">
                        <h2 className="text-h4">Detailed Metrics</h2>
                        <p className="text-caption text-surface-500">Technical performance measurements</p>
                    </div>

                    <div className="divide-y divide-surface-200 dark:divide-surface-700">
                        {metricsData.map((metric) => (
                            <div key={metric.name} className="p-4 flex items-center justify-between hover:bg-surface-50 dark:hover:bg-surface-800/30">
                                <div>
                                    <p className="font-medium">{metric.name}</p>
                                    <p className="text-caption text-surface-500">{metric.description}</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-h4 gradient-text">{metric.current}</p>
                                    {metric.trend === 'up' && (
                                        <p className="text-caption text-green-500 flex items-center justify-end gap-1">
                                            <ArrowUpRight className="w-3 h-3" />
                                            Improving
                                        </p>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
}

function MetricCard({
    icon: Icon,
    label,
    value,
    subtext,
    isGood,
}: {
    icon: any;
    label: string;
    value: string;
    subtext: string;
    isGood: boolean;
}) {
    return (
        <div className="card p-4">
            <div className="flex items-center gap-2 mb-2">
                <Icon className={`w-5 h-5 ${isGood ? 'text-green-500' : 'text-yellow-500'}`} />
                <span className="text-caption text-surface-500">{label}</span>
            </div>
            <p className="text-h2 gradient-text mb-1">{value}</p>
            <p className="text-caption text-surface-400">{subtext}</p>
        </div>
    );
}

const mockQueryData = [60, 45, 30, 25, 35, 50, 70, 85];

const strategies = [
    {
        name: 'Document Search',
        percentage: 80,
        color: 'bg-gradient-to-r from-primary-500 to-primary-400',
        description: 'Searching through your uploaded files',
    },
    {
        name: 'Connection Analysis',
        percentage: 15,
        color: 'bg-gradient-to-r from-accent-500 to-accent-400',
        description: 'Finding relationships between topics',
    },
    {
        name: 'Web Search',
        percentage: 5,
        color: 'bg-gradient-to-r from-surface-400 to-surface-300',
        description: 'Looking up current information online',
    },
];

const metricsData = [
    { name: 'Answer Accuracy', current: '92%', description: 'How often answers are correct', trend: 'up' },
    { name: 'Source Reliability', current: '96%', description: 'Answers grounded in your documents', trend: 'up' },
    { name: 'Topic Coverage', current: '88%', description: 'Finding all relevant information', trend: 'up' },
    { name: 'Response Speed', current: '1.2s', description: 'Time to generate answers', trend: 'up' },
];
