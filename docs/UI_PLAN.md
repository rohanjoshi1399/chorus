# Multi-Agent RAG UI Implementation Plan

## Overview

A modern React-based dashboard for the Multi-Agent RAG system with real-time chat, document management, and system monitoring.

---

## UI Design

### Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | Next.js 14 | App Router, SSR |
| UI Library | shadcn/ui | Modern components |
| Styling | Tailwind CSS | Utility-first |
| State | Zustand | Lightweight |
| WebSocket | Native WS | Real-time chat |
| Charts | Recharts | Metrics viz |

---

## Page Structure

```
/                       # Landing/Dashboard
├── /chat              # Main chat interface
├── /documents         # Document management
│   ├── /upload        # Upload new docs
│   └── /[id]          # Document viewer
├── /agents            # Agent monitoring
├── /analytics         # Metrics & evaluation
└── /settings          # Configuration
```

---

## Core Components

### 1. Chat Interface

```
┌────────────────────────────────────────────┐
│  Multi-Agent RAG Chat                  [⋮] │
├────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐   │
│  │ Agent Trace: [QA] → [RT] → [RET]    │   │
│  └─────────────────────────────────────┘   │
│                                            │
│  ┌─────────────────────────────────────┐   │
│  │ 🤖 Assistant                         │   │
│  │ Here's how LangGraph handles...     │   │
│  │                                      │   │
│  │ Sources: [1] docs.langchain.com     │   │
│  │          [2] github.com/...         │   │
│  └─────────────────────────────────────┘   │
│                                            │
├────────────────────────────────────────────┤
│  ┌────────────────────────────────┐ [Send] │
│  │ Ask about LangGraph...          │       │
│  └────────────────────────────────┘        │
└────────────────────────────────────────────┘
```

**Features:**
- Real-time streaming responses
- Agent trace visualization
- Source citations with links
- Conversation history
- Session management

### 2. Document Manager

```
┌────────────────────────────────────────────┐
│  Documents                    [+ Upload]   │
├────────────────────────────────────────────┤
│  🔍 Search documents...                    │
├────────────────────────────────────────────┤
│  ┌────────────────────────────────────┐    │
│  │ 📄 langchain_docs.pdf              │    │
│  │    Chunks: 42 | Uploaded: 2h ago   │    │
│  │    [View] [Delete]                 │    │
│  └────────────────────────────────────┘    │
│  ┌────────────────────────────────────┐    │
│  │ 📄 aws_bedrock_guide.md            │    │
│  │    Chunks: 28 | Uploaded: 1d ago   │    │
│  │    [View] [Delete]                 │    │
│  └────────────────────────────────────┘    │
└────────────────────────────────────────────┘
```

**Features:**
- Drag-and-drop upload
- Semantic chunking preview
- Document search
- Chunk visualization

### 3. Agent Monitor

```
┌────────────────────────────────────────────┐
│  Agent Activity                            │
├────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐  │
│  │   [Supervisor] ──► [Query Analyzer]  │  │
│  │         │                            │  │
│  │         ▼                            │  │
│  │     [Router] ──┬── [Retrieval]       │  │
│  │                └── [Graph Query]     │  │
│  │         │                            │  │
│  │         ▼                            │  │
│  │    [Validator] ──► [Synthesis]       │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  Active Sessions: 3                        │
│  Avg Latency: 1.2s                         │
│  Success Rate: 98%                         │
└────────────────────────────────────────────┘
```

### 4. Analytics Dashboard

```
┌────────────────────────────────────────────┐
│  RAG Metrics                   [Export]    │
├────────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ P@5     │ │ MRR     │ │ Faithful│       │
│  │  92%    │ │  0.84   │ │  96%    │       │
│  └─────────┘ └─────────┘ └─────────┘       │
│                                            │
│  [Chart: Query Latency over Time]          │
│  ▁▂▃▄▃▂▃▄▅▄▃▂▃▄▃                          │
│                                            │
│  [Chart: Retrieval Strategy Usage]         │
│  ████████░░ Vector (80%)                   │
│  ███░░░░░░░ Graph (15%)                    │
│  █░░░░░░░░░ Web (5%)                       │
└────────────────────────────────────────────┘
```

---

## File Structure

```
ui/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Dashboard
│   ├── chat/
│   │   └── page.tsx         # Chat interface
│   ├── documents/
│   │   ├── page.tsx         # Document list
│   │   └── upload/page.tsx  # Upload form
│   ├── agents/
│   │   └── page.tsx         # Agent monitor
│   └── analytics/
│       └── page.tsx         # Metrics
├── components/
│   ├── ui/                  # shadcn components
│   ├── chat/
│   │   ├── ChatWindow.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── AgentTrace.tsx
│   │   └── SourceCard.tsx
│   ├── documents/
│   │   ├── DocumentCard.tsx
│   │   ├── UploadZone.tsx
│   │   └── ChunkPreview.tsx
│   └── agents/
│       ├── AgentGraph.tsx
│       └── MetricCard.tsx
├── lib/
│   ├── api.ts               # REST client
│   ├── websocket.ts         # WS connection
│   └── types.ts             # TypeScript types
├── hooks/
│   ├── useChat.ts           # Chat logic
│   └── useWebSocket.ts      # WS hook
└── stores/
    ├── chatStore.ts         # Chat state
    └── sessionStore.ts      # Session state
```

---

## WebSocket Integration

```typescript
// hooks/useWebSocket.ts
export function useWebSocket(onMessage: (msg: WSMessage) => void) {
  const [status, setStatus] = useState<'connecting'|'connected'|'error'>('connecting');
  const ws = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000/api/v1/ws/chat');
    
    ws.current.onopen = () => setStatus('connected');
    ws.current.onmessage = (e) => onMessage(JSON.parse(e.data));
    ws.current.onerror = () => setStatus('error');
    
    return () => ws.current?.close();
  }, []);
  
  const send = (message: string) => {
    ws.current?.send(JSON.stringify({
      type: 'chat.message',
      message,
    }));
  };
  
  return { status, send };
}
```

---

## Implementation Phases

### Phase 1: Core Chat (Week 1)
- [ ] Next.js project setup
- [ ] Chat interface components
- [ ] WebSocket connection
- [ ] Streaming responses
- [ ] Agent trace display

### Phase 2: Documents (Week 2)
- [ ] Document list view
- [ ] Upload with progress
- [ ] Chunk visualization
- [ ] Search functionality

### Phase 3: Monitoring (Week 3)
- [ ] Agent flow diagram
- [ ] Real-time metrics
- [ ] Session management
- [ ] Analytics charts

### Phase 4: Polish (Week 4)
- [ ] Dark/light mode
- [ ] Mobile responsive
- [ ] Error handling
- [ ] Loading states

---

## Quick Start Commands

```bash
# Create Next.js project
npx create-next-app@latest ui --typescript --tailwind --app --src-dir

# Add shadcn/ui
npx shadcn-ui@latest init

# Install dependencies
cd ui
npm install zustand recharts @tanstack/react-query
```

---

## Design Principles

1. **Real-time First**: WebSocket for all chat interactions
2. **Progressive Disclosure**: Show agent details on demand
3. **Source Transparency**: Always display citation sources
4. **Performance**: Virtualized lists, lazy loading
5. **Accessibility**: ARIA labels, keyboard navigation
