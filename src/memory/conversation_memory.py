"""
Conversation memory with Redis backend.

Provides:
- Session-based conversation storage
- Message history retrieval
- Context compression for long conversations
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import redis.asyncio as redis

from ..config import settings


class ConversationMemory:
    """
    Redis-backed conversation memory for multi-turn chat.
    """
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis = None
        self.session_ttl = 60 * 60 * 24  # 24 hours
        self.max_messages = settings.memory_buffer_size
    
    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self.redis is None:
            self.redis = redis.from_url(
                settings.redis_url,
                password=settings.redis_password or None,
                decode_responses=True,
            )
        return self.redis
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a message to conversation history.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant)
            content: Message content
            metadata: Optional metadata
        """
        r = await self._get_redis()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        
        key = f"conversation:{session_id}"
        await r.rpush(key, json.dumps(message))
        await r.expire(key, self.session_ttl)
        
        # Trim to max messages
        await r.ltrim(key, -self.max_messages, -1)
    
    async def get_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, str]]:
        """
        Get conversation history.
        
        Args:
            session_id: Session identifier
            limit: Optional limit on messages
            
        Returns:
            List of messages
        """
        r = await self._get_redis()
        key = f"conversation:{session_id}"
        
        if limit:
            messages = await r.lrange(key, -limit, -1)
        else:
            messages = await r.lrange(key, 0, -1)
        
        return [json.loads(m) for m in messages]
    
    async def get_context_window(
        self,
        session_id: str,
        max_tokens: int = 4000,
    ) -> List[Dict[str, str]]:
        """
        Get recent conversation context within token limit.
        
        Args:
            session_id: Session identifier
            max_tokens: Approximate max token count
            
        Returns:
            Recent messages within token budget
        """
        history = await self.get_history(session_id)
        
        # Simple token estimation (4 chars ~= 1 token)
        result = []
        total_chars = 0
        char_limit = max_tokens * 4
        
        for message in reversed(history):
            content_len = len(message.get("content", ""))
            if total_chars + content_len > char_limit:
                break
            result.insert(0, message)
            total_chars += content_len
        
        return result
    
    async def clear_session(self, session_id: str) -> None:
        """Clear a session's conversation history."""
        r = await self._get_redis()
        await r.delete(f"conversation:{session_id}")
    
    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()


# Global memory instance
conversation_memory = ConversationMemory()
