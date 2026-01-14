# Multi-Agent RAG UI

Modern React dashboard for the Multi-Agent RAG system.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Icons**: Lucide React
- **Animations**: Framer Motion

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Pages

| Route | Description |
|-------|-------------|
| `/` | Landing page with feature overview |
| `/chat` | Real-time chat with WebSocket |
| `/documents` | Document management |
| `/agents` | Agent monitoring dashboard |
| `/analytics` | RAG metrics and evaluations |

## Features

- 🎨 Cool blue/teal color palette
- 🌙 Dark mode by default
- 📱 Fully responsive design
- ⚡ Real-time WebSocket chat
- 🔄 Agent trace visualization
- 📊 RAG metrics dashboard

## Environment Variables

```bash
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/ws/chat
```

## Design System

- **Typography**: Inter (sans), JetBrains Mono (code)
- **Colors**: Primary (sky blue), Accent (teal), Surface (slate)
- **Effects**: Glassmorphism, gradient text, soft shadows
