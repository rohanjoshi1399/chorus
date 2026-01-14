import Link from 'next/link';
import { MessageSquare, FileText, Activity, BarChart3, Sparkles, ArrowRight, Database, GitBranch, Layers, Search, Shield, Zap, CheckCircle2, XCircle } from 'lucide-react';

export default function HomePage() {
    return (
        <main className="min-h-screen">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-surface-200/50 dark:border-surface-700/50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                                <Sparkles className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-h4 font-semibold">Chorus: A Multi-Agent RAG System</span>
                        </div>

                        <div className="hidden md:flex items-center gap-1">
                            <Link href="/chat" className="btn-ghost">
                                <MessageSquare className="w-4 h-4" />
                                Chat
                            </Link>
                            <Link href="/documents" className="btn-ghost">
                                <FileText className="w-4 h-4" />
                                Documents
                            </Link>
                            <Link href="/agents" className="btn-ghost">
                                <Activity className="w-4 h-4" />
                                Agents
                            </Link>
                            <Link href="/analytics" className="btn-ghost">
                                <BarChart3 className="w-4 h-4" />
                                Analytics
                            </Link>
                        </div>

                        <div className="md:hidden">
                            <Link href="/chat" className="btn-primary">
                                Chat
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section - Split Layout */}
            <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-7xl mx-auto">
                    <div className="grid lg:grid-cols-2 gap-12 items-center">
                        {/* Left: Content */}
                        <div>
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 text-primary-600 dark:text-primary-400 text-body-sm font-medium mb-6">
                                <Sparkles className="w-4 h-4" />
                                Retrieval-Augmented Generation
                            </div>

                            <h1 className="text-display gradient-text mb-6">
                                Document-Grounded<br />Question Answering
                            </h1>

                            <p className="text-body-lg text-surface-600 dark:text-surface-400 mb-8">
                                A production RAG system with multi-agent orchestration, hybrid retrieval,
                                and knowledge graph integration. Every answer is grounded in your documents
                                with verifiable sources.
                            </p>

                            <div className="flex flex-col sm:flex-row gap-4 mb-8">
                                <Link href="/chat" className="btn-primary text-body px-6 py-3">
                                    <MessageSquare className="w-5 h-5" />
                                    Open Chat
                                    <ArrowRight className="w-4 h-4" />
                                </Link>
                                <Link href="/documents" className="btn-secondary text-body px-6 py-3">
                                    <FileText className="w-5 h-5" />
                                    Manage Documents
                                </Link>
                            </div>

                            {/* Quick Stats */}
                            <div className="grid grid-cols-3 gap-4">
                                <div>
                                    <p className="text-h3 gradient-text">90%+</p>
                                    <p className="text-caption text-surface-500">Target Precision</p>
                                </div>
                                <div>
                                    <p className="text-h3 gradient-text">9</p>
                                    <p className="text-caption text-surface-500">Specialized Agents</p>
                                </div>
                                <div>
                                    <p className="text-h3 gradient-text">~1-2s</p>
                                    <p className="text-caption text-surface-500">Typical Response</p>
                                </div>
                            </div>
                        </div>

                        {/* Right: Visual Flow Diagram */}
                        <div className="relative">
                            <div className="card p-8 space-y-4">
                                <h3 className="text-h4 mb-6 text-center">Query Processing Flow</h3>

                                {visualFlow.map((step, index) => (
                                    <div key={index} className="relative">
                                        <div className="flex items-center gap-4">
                                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${step.type === 'input' ? 'bg-primary-500 text-white' :
                                                step.type === 'process' ? 'bg-accent-500/20 text-accent-600 dark:text-accent-400' :
                                                    'bg-green-500 text-white'
                                                }`}>
                                                <step.icon className="w-5 h-5" />
                                            </div>
                                            <div className="flex-1">
                                                <p className="font-medium text-body-sm">{step.label}</p>
                                                <p className="text-caption text-surface-500">{step.agent}</p>
                                            </div>
                                        </div>
                                        {index < visualFlow.length - 1 && (
                                            <div className="ml-5 h-6 w-px bg-gradient-to-b from-surface-300 to-transparent dark:from-surface-600" />
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Comparison Table - RAG vs Standard LLM */}
            <section className="py-20 px-4 sm:px-6 lg:px-8 bg-surface-100/50 dark:bg-surface-900/50">
                <div className="max-w-5xl mx-auto">
                    <h2 className="text-h2 text-center mb-4">RAG vs Standard Chat Assistants</h2>
                    <p className="text-body text-surface-500 text-center mb-12">
                        How retrieval-augmented generation differs from general-purpose LLMs
                    </p>

                    <div className="card overflow-hidden">
                        <table className="w-full">
                            <thead>
                                <tr className="bg-surface-50 dark:bg-surface-800/50">
                                    <th className="text-left px-6 py-4 font-medium text-surface-900 dark:text-surface-100">Capability</th>
                                    <th className="text-center px-6 py-4 font-medium text-red-600 dark:text-red-400">Standard LLM</th>
                                    <th className="text-center px-6 py-4 font-medium text-green-600 dark:text-green-400">This System</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-surface-200 dark:divide-surface-700">
                                {comparison.map((row, index) => (
                                    <tr key={index} className="hover:bg-surface-50 dark:hover:bg-surface-800/30">
                                        <td className="px-6 py-4">
                                            <p className="font-medium">{row.feature}</p>
                                            <p className="text-caption text-surface-500">{row.description}</p>
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            <div className="flex flex-col items-center gap-1">
                                                <XCircle className="w-5 h-5 text-red-500" />
                                                <span className="text-body-sm text-surface-600 dark:text-surface-400">{row.standard}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            <div className="flex flex-col items-center gap-1">
                                                <CheckCircle2 className="w-5 h-5 text-green-500" />
                                                <span className="text-body-sm text-surface-600 dark:text-surface-400">{row.rag}</span>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            {/* Architecture Components - Card Grid */}
            <section className="py-20 px-4 sm:px-6 lg:px-8">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-12">
                        <h2 className="text-h2 mb-4">System Components</h2>
                        <p className="text-body text-surface-500 max-w-2xl mx-auto">
                            Production-grade architecture built for accuracy, speed, and scalability
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {architecture.map((component, index) => (
                            <div key={index} className="card-hover p-6 group relative overflow-hidden">
                                {/* Gradient accent */}
                                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-primary-500/10 to-accent-500/10 rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity" />

                                <div className="relative">
                                    <div className="flex items-center gap-3 mb-4">
                                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center group-hover:shadow-glow transition-shadow duration-300">
                                            <component.icon className="w-6 h-6 text-primary-500" />
                                        </div>
                                        <h3 className="text-h4">{component.title}</h3>
                                    </div>

                                    <p className="text-body-sm text-surface-600 dark:text-surface-400 mb-4">
                                        {component.description}
                                    </p>

                                    <div className="flex items-center gap-2">
                                        <div className="px-2.5 py-1 rounded-full bg-surface-100 dark:bg-surface-800 text-caption font-mono">
                                            {component.tech}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Technical Highlights - Bento Grid */}
            <section className="py-20 px-4 sm:px-6 lg:px-8 bg-surface-100/50 dark:bg-surface-900/50">
                <div className="max-w-7xl mx-auto">
                    <h2 className="text-h2 text-center mb-12">Technical Highlights</h2>

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* Large card */}
                        <div className="lg:col-span-2 lg:row-span-2 card p-8">
                            <div className="h-full flex flex-col justify-between">
                                <div>
                                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center mb-4">
                                        <GitBranch className="w-7 h-7 text-primary-500" />
                                    </div>
                                    <h3 className="text-h3 mb-3">Multi-Agent Orchestration</h3>
                                    <p className="text-body text-surface-600 dark:text-surface-400 mb-4">
                                        9 specialized agents (1 orchestrator + 5 L2 processors + 3 L3 retrievers)
                                        coordinated via LangGraph StateGraph with conditional routing and state persistence.
                                    </p>
                                </div>
                                <div className="space-y-2">
                                    <div className="flex items-center gap-2 text-body-sm">
                                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                                        <span>Hierarchical delegation (L1→L2→L3)</span>
                                    </div>
                                    <div className="flex items-center gap-2 text-body-sm">
                                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                                        <span>Parallel execution with asyncio.gather</span>
                                    </div>
                                    <div className="flex items-center gap-2 text-body-sm">
                                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                                        <span>Cycle support for query refinement</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Small cards */}
                        <div className="card p-6">
                            <Search className="w-8 h-8 text-primary-500 mb-3" />
                            <h4 className="text-h4 mb-2">Hybrid Retrieval</h4>
                            <p className="text-body-sm text-surface-500">
                                Dense vector + sparse BM25 with RRF
                            </p>
                        </div>

                        <div className="card p-6">
                            <Shield className="w-8 h-8 text-primary-500 mb-3" />
                            <h4 className="text-h4 mb-2">Query Rewrite Loop</h4>
                            <p className="text-body-sm text-surface-500">
                                Iterative refinement (max 2 rewrites)
                            </p>
                        </div>

                        <div className="card p-6">
                            <Database className="w-8 h-8 text-primary-500 mb-3" />
                            <h4 className="text-h4 mb-2">Knowledge Graph</h4>
                            <p className="text-body-sm text-surface-500">
                                Neo4j for entity relationships
                            </p>
                        </div>

                        <div className="card p-6">
                            <Layers className="w-8 h-8 text-primary-500 mb-3" />
                            <h4 className="text-h4 mb-2">Semantic Chunking</h4>
                            <p className="text-body-sm text-surface-500">
                                Max-Min cosine similarity clustering
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-12 px-4 border-t border-surface-200/50 dark:border-surface-800/50">
                <div className="max-w-7xl mx-auto">
                    <div className="grid md:grid-cols-3 gap-8 mb-8">
                        <div>
                            <div className="flex items-center gap-2 mb-3">
                                <Sparkles className="w-5 h-5 text-primary-500" />
                                <span className="font-semibold">Multi-Agent RAG</span>
                            </div>
                            <p className="text-body-sm text-surface-500">
                                Production-ready retrieval-augmented generation with hierarchical agent orchestration.
                            </p>
                        </div>

                        <div>
                            <h4 className="font-medium mb-3">Navigation</h4>
                            <div className="space-y-2 text-body-sm text-surface-500">
                                <Link href="/chat" className="block hover:text-primary-500 transition-colors">Chat Interface</Link>
                                <Link href="/documents" className="block hover:text-primary-500 transition-colors">Documents</Link>
                                <Link href="/agents" className="block hover:text-primary-500 transition-colors">Agents</Link>
                                <Link href="/analytics" className="block hover:text-primary-500 transition-colors">Analytics</Link>
                            </div>
                        </div>

                        <div>
                            <h4 className="font-medium mb-3">Technology Stack</h4>
                            <div className="flex flex-wrap gap-2">
                                {['LangGraph', 'Claude 4.5', 'Qdrant', 'Neo4j', 'Redis', 'BGE'].map((tech) => (
                                    <span key={tech} className="px-2.5 py-1 rounded-full bg-surface-100 dark:bg-surface-800 text-caption">
                                        {tech}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="pt-8 border-t border-surface-200/50 dark:border-surface-700/50 text-center text-caption text-surface-400">
                        Built with LangChain ecosystem • Deployed on AWS EKS
                    </div>
                </div>
            </footer>
        </main>
    );
}

const visualFlow = [
    { icon: MessageSquare, label: 'User Query', agent: 'Input', type: 'input' },
    { icon: Search, label: 'Analyze Intent', agent: 'QueryAnalyzerAgent', type: 'process' },
    { icon: GitBranch, label: 'Route Strategy', agent: 'RouterAgent', type: 'process' },
    { icon: Database, label: 'Parallel Retrieval', agent: 'Retrieval/Graph/Web Agents', type: 'process' },
    { icon: Shield, label: 'Grade & Rewrite', agent: 'QueryRewriterAgent', type: 'process' },
    { icon: CheckCircle2, label: 'Validate & Synthesize', agent: 'Validator + Synthesis', type: 'output' },
];

const comparison = [
    {
        feature: 'Information Source',
        description: 'Where answers come from',
        standard: 'Pre-training corpus',
        rag: 'Your uploaded documents',
    },
    {
        feature: 'Source Attribution',
        description: 'Verifiable citations',
        standard: 'No citations',
        rag: 'Exact passage links',
    },
    {
        feature: 'Retrieval Strategy',
        description: 'How information is found',
        standard: 'No retrieval',
        rag: 'Hybrid (vector + BM25 + reranking)',
    },
    {
        feature: 'Quality Assurance',
        description: 'Answer verification',
        standard: 'Single generation',
        rag: 'Iterative grading & rewrite',
    },
];

const architecture = [
    {
        icon: Layers,
        title: 'Semantic Chunking',
        description: 'Max-Min algorithm clusters sentences by cosine similarity to preserve semantic boundaries.',
        tech: 'Titan Embeddings V2',
    },
    {
        icon: Database,
        title: 'Vector Store',
        description: 'Dense embeddings with HNSW indexing for approximate nearest neighbor search at scale.',
        tech: 'Qdrant',
    },
    {
        icon: GitBranch,
        title: 'Knowledge Graph',
        description: 'LLM-based entity extraction with Neo4j storage for multi-hop relationship queries.',
        tech: 'Neo4j + Cypher',
    },
    {
        icon: Search,
        title: 'Cross-Encoder Reranking',
        description: 'BGE-Reranker-Large transformer model for second-stage precision improvement.',
        tech: 'sentence-transformers',
    },
    {
        icon: Activity,
        title: 'LangGraph Workflow',
        description: 'Stateful orchestration with conditional edges, cycles, and Redis checkpointing.',
        tech: 'StateGraph',
    },
    {
        icon: Zap,
        title: 'LLM Generation',
        description: 'Claude 4.5 Sonnet via AWS Bedrock for reasoning, analysis, and synthesis.',
        tech: 'Bedrock',
    },
];
