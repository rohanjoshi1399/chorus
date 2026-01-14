'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import {
    Send,
    Sparkles,
    ArrowLeft,
    ExternalLink,
    Copy,
    Check,
    Loader2,
    MessageSquare,
    HelpCircle,
    RefreshCw,
} from 'lucide-react';
import { useChat } from '@/hooks/useChat';

export default function ChatPage() {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);

    const { messages, isLoading, agentTrace, sendMessage, connectionStatus } = useChat();

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Focus input on mount
    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        sendMessage(input);
        setInput('');
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        setInput(suggestion);
        inputRef.current?.focus();
    };

    return (
        <div className="flex flex-col h-screen">
            {/* Header */}
            <header className="flex-shrink-0 glass border-b border-surface-200/50 dark:border-surface-700/50">
                <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="btn-ghost p-2" title="Back to home">
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <div className="flex items-center gap-3">
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                                <MessageSquare className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h1 className="text-h4 font-semibold">Ask Anything</h1>
                                <div className="flex items-center gap-2 text-caption text-surface-500">
                                    <span className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-green-500' :
                                            connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' :
                                                'bg-red-500'
                                        }`} />
                                    {connectionStatus === 'connected' ? 'Ready' :
                                        connectionStatus === 'connecting' ? 'Connecting...' :
                                            'Offline'}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Agent Progress - simplified for users */}
                    {isLoading && agentTrace.length > 0 && (
                        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary-500/10">
                            <Loader2 className="w-3 h-3 animate-spin text-primary-500" />
                            <span className="text-caption text-primary-600 dark:text-primary-400">
                                {getAgentFriendlyName(agentTrace[agentTrace.length - 1])}
                            </span>
                        </div>
                    )}
                </div>
            </header>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto">
                <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
                    {messages.length === 0 ? (
                        <EmptyState onSuggestionClick={handleSuggestionClick} />
                    ) : (
                        messages.map((message, index) => (
                            <MessageBubble key={index} message={message} />
                        ))
                    )}

                    {isLoading && (
                        <div className="flex items-start gap-3 animate-in">
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center flex-shrink-0">
                                <Sparkles className="w-4 h-4 text-white" />
                            </div>
                            <div className="flex flex-col gap-2">
                                <div className="flex items-center gap-2 px-4 py-3 message-assistant">
                                    <div className="typing-dot" style={{ animationDelay: '0ms' }} />
                                    <div className="typing-dot" style={{ animationDelay: '150ms' }} />
                                    <div className="typing-dot" style={{ animationDelay: '300ms' }} />
                                </div>
                                <span className="text-caption text-surface-400 pl-1">
                                    Searching your documents...
                                </span>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <div className="flex-shrink-0 border-t border-surface-200/50 dark:border-surface-700/50 glass">
                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto px-4 py-4">
                    <div className="relative flex items-end gap-3">
                        <div className="flex-1 relative">
                            <textarea
                                ref={inputRef}
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask a question about your documents..."
                                rows={1}
                                className="input resize-none min-h-[52px] max-h-32 pr-12"
                                style={{ height: 'auto' }}
                                aria-label="Type your question"
                                onInput={(e) => {
                                    const target = e.target as HTMLTextAreaElement;
                                    target.style.height = 'auto';
                                    target.style.height = Math.min(target.scrollHeight, 128) + 'px';
                                }}
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="btn-primary h-[52px] w-[52px] p-0 flex-shrink-0"
                            aria-label="Send message"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Send className="w-5 h-5" />
                            )}
                        </button>
                    </div>

                    <p className="text-caption text-surface-400 mt-2 text-center">
                        Press Enter to send • Shift+Enter for new line
                    </p>
                </form>
            </div>
        </div>
    );
}

function EmptyState({ onSuggestionClick }: { onSuggestionClick: (s: string) => void }) {
    return (
        <div className="flex flex-col items-center justify-center py-12 md:py-20 text-center px-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center mb-6">
                <Sparkles className="w-8 h-8 text-primary-500" />
            </div>
            <h2 className="text-h3 mb-2">What would you like to know?</h2>
            <p className="text-body text-surface-500 max-w-md mb-8">
                Ask any question about your uploaded documents. I'll find the answer and show you where it came from.
            </p>

            {/* Suggestions */}
            <div className="w-full max-w-lg">
                <p className="text-caption text-surface-400 mb-3">Try asking:</p>
                <div className="flex flex-col gap-2">
                    {suggestions.map((suggestion, i) => (
                        <button
                            key={i}
                            onClick={() => onSuggestionClick(suggestion)}
                            className="card-hover p-4 text-left hover:border-primary-300 dark:hover:border-primary-700 transition-colors"
                        >
                            <span className="text-body">{suggestion}</span>
                        </button>
                    ))}
                </div>
            </div>

            {/* Help tip */}
            <div className="mt-8 p-4 rounded-xl bg-surface-100/50 dark:bg-surface-800/50 max-w-md">
                <div className="flex items-start gap-3">
                    <HelpCircle className="w-5 h-5 text-surface-400 flex-shrink-0 mt-0.5" />
                    <p className="text-body-sm text-surface-500 text-left">
                        <strong>Tip:</strong> The more specific your question, the better the answer.
                        Ask about details, comparisons, or summaries.
                    </p>
                </div>
            </div>
        </div>
    );
}

interface Message {
    role: 'user' | 'assistant';
    content: string;
    sources?: Array<{ title: string; url: string }>;
    metadata?: {
        confidence?: number;
        strategies?: string[];
        rewrites?: number;
    };
}

function MessageBubble({ message }: { message: Message }) {
    const [copied, setCopied] = useState(false);

    const copyToClipboard = async () => {
        await navigator.clipboard.writeText(message.content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (message.role === 'user') {
        return (
            <div className="flex justify-end animate-in">
                <div className="max-w-[85%] md:max-w-[70%]">
                    <div className="message-user px-4 py-3 shadow-soft">
                        <p className="text-body whitespace-pre-wrap">{message.content}</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="flex gap-3 animate-in">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center flex-shrink-0 mt-1">
                <Sparkles className="w-4 h-4 text-white" />
            </div>

            <div className="flex-1 max-w-[85%] md:max-w-[75%]">
                <div className="message-assistant px-4 py-3 shadow-soft">
                    <p className="text-body whitespace-pre-wrap leading-relaxed">{message.content}</p>
                </div>

                {/* Sources - user friendly */}
                {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 space-y-2">
                        <p className="text-caption text-surface-500 font-medium flex items-center gap-1">
                            <ExternalLink className="w-3 h-3" />
                            Sources used:
                        </p>
                        <div className="flex flex-wrap gap-2">
                            {message.sources.map((source, i) => (
                                <a
                                    key={i}
                                    href={source.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-100 dark:bg-surface-800 text-body-sm text-primary-600 dark:text-primary-400 hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors"
                                >
                                    <span className="truncate max-w-[180px]">{source.title}</span>
                                    <ExternalLink className="w-3 h-3 flex-shrink-0" />
                                </a>
                            ))}
                        </div>
                    </div>
                )}

                {/* Confidence indicator - only show if high */}
                {message.metadata?.confidence && message.metadata.confidence >= 0.9 && (
                    <div className="mt-2 flex items-center gap-1 text-caption text-green-600 dark:text-green-400">
                        <Check className="w-3 h-3" />
                        High confidence answer
                    </div>
                )}

                {/* Copy button */}
                <div className="mt-2 flex items-center gap-2">
                    <button
                        onClick={copyToClipboard}
                        className="btn-ghost p-1.5 text-surface-400 hover:text-surface-600"
                        title="Copy answer"
                    >
                        {copied ? (
                            <Check className="w-4 h-4 text-green-500" />
                        ) : (
                            <Copy className="w-4 h-4" />
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}

// Convert agent names to user-friendly labels
function getAgentFriendlyName(agent: string): string {
    const names: Record<string, string> = {
        'supervisor': 'Starting...',
        'query_analyzer': 'Understanding question',
        'router': 'Choosing strategy',
        'multi_retrieval': 'Searching documents',
        'retrieval': 'Searching documents',
        'graph_query': 'Finding connections',
        'web_search': 'Checking web',
        'grade_results': 'Checking results',
        'rewrite_query': 'Refining search',
        'validator': 'Verifying facts',
        'synthesis': 'Writing answer',
    };
    return names[agent] || 'Working...';
}

const suggestions = [
    "What are the main topics covered in my documents?",
    "Summarize the key points about [topic]",
    "How does [concept A] relate to [concept B]?",
];
