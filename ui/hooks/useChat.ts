'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

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

interface WSMessage {
    type: string;
    session_id?: string;
    agent?: string;
    message?: string;
    answer?: string;
    sources?: Array<{ title: string; url: string }>;
    metadata?: Record<string, any>;
}

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/v1/ws/chat';

export function useChat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [agentTrace, setAgentTrace] = useState<string[]>([]);
    const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');
    const [sessionId, setSessionId] = useState<string | null>(null);

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        setConnectionStatus('connecting');

        try {
            wsRef.current = new WebSocket(WS_URL);

            wsRef.current.onopen = () => {
                console.log('WebSocket connected');
                setConnectionStatus('connected');
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const data: WSMessage = JSON.parse(event.data);
                    handleMessage(data);
                } catch (e) {
                    console.error('Failed to parse message:', e);
                }
            };

            wsRef.current.onclose = () => {
                console.log('WebSocket disconnected');
                setConnectionStatus('disconnected');
                // Attempt reconnect after 3 seconds
                reconnectTimeoutRef.current = setTimeout(connect, 3000);
            };

            wsRef.current.onerror = (error) => {
                console.error('WebSocket error:', error);
                setConnectionStatus('disconnected');
            };
        } catch (error) {
            console.error('Failed to connect:', error);
            setConnectionStatus('disconnected');
        }
    }, []);

    const handleMessage = (data: WSMessage) => {
        switch (data.type) {
            case 'session.created':
                setSessionId(data.session_id || null);
                break;

            case 'agent.thinking':
                if (data.agent) {
                    setAgentTrace((prev) => [...new Set([...prev, data.agent!])]);
                }
                break;

            case 'retrieval.progress':
                // Could update a progress indicator here
                break;

            case 'message.complete':
                setMessages((prev) => [
                    ...prev,
                    {
                        role: 'assistant',
                        content: data.answer || '',
                        sources: data.sources,
                        metadata: data.metadata as Message['metadata'],
                    },
                ]);
                setIsLoading(false);
                setAgentTrace([]);
                break;

            case 'message.stream':
                // For streaming updates - append to last message
                if (data.message) {
                    setMessages((prev) => {
                        const last = prev[prev.length - 1];
                        if (last && last.role === 'assistant') {
                            return [
                                ...prev.slice(0, -1),
                                { ...last, content: last.content + data.message },
                            ];
                        }
                        return [...prev, { role: 'assistant', content: data.message! }];
                    });
                }
                break;

            case 'error':
                console.error('Server error:', data.message);
                setIsLoading(false);
                setMessages((prev) => [
                    ...prev,
                    {
                        role: 'assistant',
                        content: `Error: ${data.message || 'An error occurred'}`,
                    },
                ]);
                break;
        }
    };

    const sendMessage = useCallback((content: string) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
            console.error('WebSocket not connected');
            return;
        }

        // Add user message immediately
        setMessages((prev) => [...prev, { role: 'user', content }]);
        setIsLoading(true);
        setAgentTrace([]);

        // Send to server
        wsRef.current.send(
            JSON.stringify({
                type: 'chat.message',
                session_id: sessionId,
                message: content,
            })
        );
    }, [sessionId]);

    // Connect on mount
    useEffect(() => {
        connect();

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect]);

    return {
        messages,
        isLoading,
        agentTrace,
        connectionStatus,
        sessionId,
        sendMessage,
    };
}
