'use client';

import Link from 'next/link';
import {
    ArrowLeft,
    Activity,
    Cpu,
    Zap,
    Clock,
    CheckCircle,
    XCircle,
    HelpCircle,
    ChevronRight,
} from 'lucide-react';

interface AgentStatus {
    name: string;
    friendlyName: string;
    description: string;
    level: number;
    status: 'active' | 'idle' | 'error';
    lastActive: string;
    calls: number;
}

export default function AgentsPage() {
    const agents = mockAgents;

    const activeCount = agents.filter(a => a.status === 'active').length;

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
                                <Activity className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h1 className="text-h4 font-semibold">AI Agents</h1>
                                <p className="text-caption text-surface-500 hidden sm:block">
                                    See how the AI processes your questions
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
                                <strong>What are agents?</strong> When you ask a question, multiple AI specialists work together
                                to find the best answer. Each agent has a specific job, like understanding your question,
                                searching documents, or writing the final answer.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
                    <div className="card p-4">
                        <div className="flex items-center gap-2 mb-1">
                            <Cpu className="w-4 h-4 text-primary-500" />
                            <span className="text-caption text-surface-500">Total Agents</span>
                        </div>
                        <p className="text-h2 gradient-text">{agents.length}</p>
                    </div>

                    <div className="card p-4">
                        <div className="flex items-center gap-2 mb-1">
                            <Zap className="w-4 h-4 text-green-500" />
                            <span className="text-caption text-surface-500">Active Now</span>
                        </div>
                        <p className="text-h2 text-green-500">{activeCount}</p>
                    </div>

                    <div className="card p-4 col-span-2 md:col-span-1">
                        <div className="flex items-center gap-2 mb-1">
                            <Clock className="w-4 h-4 text-primary-500" />
                            <span className="text-caption text-surface-500">Avg Response</span>
                        </div>
                        <p className="text-h2 gradient-text">1.2s</p>
                    </div>
                </div>

                {/* Agent Flow Visualization */}
                <div className="card p-6 mb-8">
                    <h2 className="text-h3 mb-2">How Your Question Gets Answered</h2>
                    <p className="text-body-sm text-surface-500 mb-6">
                        This is the path your question takes through our AI system
                    </p>

                    <div className="space-y-4">
                        {/* Step 1 */}
                        <div className="flex items-center gap-4">
                            <div className="w-8 h-8 rounded-full bg-primary-500 text-white flex items-center justify-center text-body-sm font-medium">
                                1
                            </div>
                            <div className="flex-1">
                                <p className="font-medium">Understand Your Question</p>
                                <p className="text-caption text-surface-500">Figure out what you're really asking</p>
                            </div>
                            <ChevronRight className="w-5 h-5 text-surface-300" />
                        </div>

                        {/* Step 2 */}
                        <div className="flex items-center gap-4">
                            <div className="w-8 h-8 rounded-full bg-primary-500 text-white flex items-center justify-center text-body-sm font-medium">
                                2
                            </div>
                            <div className="flex-1">
                                <p className="font-medium">Search for Information</p>
                                <p className="text-caption text-surface-500">Look through your documents and knowledge graphs</p>
                            </div>
                            <ChevronRight className="w-5 h-5 text-surface-300" />
                        </div>

                        {/* Step 3 */}
                        <div className="flex items-center gap-4">
                            <div className="w-8 h-8 rounded-full bg-primary-500 text-white flex items-center justify-center text-body-sm font-medium">
                                3
                            </div>
                            <div className="flex-1">
                                <p className="font-medium">Check the Results</p>
                                <p className="text-caption text-surface-500">Make sure the information is relevant</p>
                            </div>
                            <ChevronRight className="w-5 h-5 text-surface-300" />
                        </div>

                        {/* Step 4 */}
                        <div className="flex items-center gap-4">
                            <div className="w-8 h-8 rounded-full bg-accent-500 text-white flex items-center justify-center text-body-sm font-medium">
                                4
                            </div>
                            <div className="flex-1">
                                <p className="font-medium">Write Your Answer</p>
                                <p className="text-caption text-surface-500">Put together a clear, helpful response</p>
                            </div>
                            <CheckCircle className="w-5 h-5 text-green-500" />
                        </div>
                    </div>
                </div>

                {/* Agent Details */}
                <div className="card overflow-hidden">
                    <div className="p-4 border-b border-surface-200 dark:border-surface-700">
                        <h2 className="text-h4">All Agents</h2>
                        <p className="text-caption text-surface-500">Detailed view of each AI specialist</p>
                    </div>

                    <div className="divide-y divide-surface-200 dark:divide-surface-700">
                        {agents.map(agent => (
                            <div key={agent.name} className="p-4 hover:bg-surface-50 dark:hover:bg-surface-800/30 transition-colors">
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="font-medium">{agent.friendlyName}</span>
                                            <StatusBadge status={agent.status} />
                                        </div>
                                        <p className="text-body-sm text-surface-500">{agent.description}</p>
                                    </div>
                                    <div className="text-right flex-shrink-0">
                                        <p className="text-body-sm font-medium">{agent.calls.toLocaleString()} uses</p>
                                        <p className="text-caption text-surface-400">{agent.lastActive}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
}

function StatusBadge({ status }: { status: AgentStatus['status'] }) {
    const config = {
        active: { icon: CheckCircle, text: 'Active', class: 'bg-green-500/10 text-green-600 dark:text-green-400' },
        idle: { icon: Clock, text: 'Standby', class: 'bg-surface-500/10 text-surface-600 dark:text-surface-400' },
        error: { icon: XCircle, text: 'Error', class: 'bg-red-500/10 text-red-600 dark:text-red-400' },
    };

    const { icon: Icon, text, class: className } = config[status];

    return (
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-caption ${className}`}>
            <Icon className="w-3 h-3" />
            {text}
        </span>
    );
}

const mockAgents: AgentStatus[] = [
    {
        name: 'supervisor',
        friendlyName: 'Coordinator',
        description: 'Manages the overall process and decides which agents to use',
        level: 1,
        status: 'active',
        calls: 1250,
        lastActive: 'Just now'
    },
    {
        name: 'query_analyzer',
        friendlyName: 'Question Analyzer',
        description: 'Understands what you\'re really asking and identifies key topics',
        level: 2,
        status: 'active',
        calls: 1180,
        lastActive: 'Just now'
    },
    {
        name: 'router',
        friendlyName: 'Strategy Picker',
        description: 'Decides the best way to find your answer',
        level: 2,
        status: 'active',
        calls: 1180,
        lastActive: 'Just now'
    },
    {
        name: 'query_rewriter',
        friendlyName: 'Search Optimizer',
        description: 'Improves search queries when initial results aren\'t good enough',
        level: 2,
        status: 'idle',
        calls: 320,
        lastActive: '5 min ago'
    },
    {
        name: 'validator',
        friendlyName: 'Fact Checker',
        description: 'Verifies information is accurate before including it',
        level: 2,
        status: 'active',
        calls: 1050,
        lastActive: 'Just now'
    },
    {
        name: 'synthesis',
        friendlyName: 'Answer Writer',
        description: 'Combines information into a clear, helpful response',
        level: 2,
        status: 'active',
        calls: 1050,
        lastActive: 'Just now'
    },
    {
        name: 'retrieval',
        friendlyName: 'Document Searcher',
        description: 'Finds relevant passages in your uploaded documents',
        level: 3,
        status: 'active',
        calls: 1100,
        lastActive: 'Just now'
    },
    {
        name: 'graph_query',
        friendlyName: 'Connection Finder',
        description: 'Discovers relationships between concepts across documents',
        level: 3,
        status: 'idle',
        calls: 280,
        lastActive: '10 min ago'
    },
    {
        name: 'web_search',
        friendlyName: 'Web Researcher',
        description: 'Searches the web for current information when needed',
        level: 3,
        status: 'idle',
        calls: 150,
        lastActive: '1 hour ago'
    },
];
