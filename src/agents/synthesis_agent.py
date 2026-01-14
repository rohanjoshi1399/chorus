"""
Synthesis Agent (Level 2) - Response composer.

Responsibilities:
- Compose coherent response from validated facts
- Integrate information from multiple sources
- Generate proper citations
- Stream response token-by-token via WebSocket
- Include code examples
- Format with markdown
"""

from typing import Any, Dict, List

from .base_agent import AgentInput, AgentOutput, BaseAgent


class SynthesisAgent(BaseAgent):
    """
    Level 2 agent that generates final user-facing responses.
    """
    
    def __init__(self, llm=None, **kwargs):
        super().__init__(
            name="synthesis",
            description="Generates final response with citations",
            level=2,
            **kwargs
        )
        self.llm = llm
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Synthesize final response from retrieved context.
        
        Response structure:
        - Direct answer
        - Detailed explanation
        - Code examples (if applicable)
        - Sources with citations
        
        Returns:
            Formatted markdown response
        """
        from ..llm import bedrock_client
        
        query = input_data.query
        context = input_data.context
        
        # Get retrieved documents from context
        retrieved_docs = context.get("retrieved_documents", [])
        
        if not retrieved_docs:
            # No context available
            response = {
                "answer": "I don't have enough information to answer this question accurately.",
                "sources": [],
                "code_examples": []
            }
            return AgentOutput(result=response, metadata={"agent": self.name}, confidence_score=0.1)
        
        # Build context from retrieved documents
        context_text = "\n\n".join([
            f"[Document {i+1}]\n{doc['text'][:500]}..."  # Limit context length
            for i, doc in enumerate(retrieved_docs[:5])  # Top 5 docs
        ])
        
        # Generate response
        synthesis_prompt = f"""Using the context provided, answer the user's question comprehensively.

User Question: "{query}"

Context:
{context_text}

Provide:
1. A direct, clear answer
2. Detailed explanation if needed
3. Code examples if relevant
4. Keep your response well-structured and professional

Format your response in clear markdown. Be factual and cite the context."""

        try:
            answer = await bedrock_client.generate(
                prompt=synthesis_prompt,
                system_prompt="You are a helpful technical assistant. Provide accurate, well-structured answers based on the given context.",
                temperature=0.1,
            )
            
            # Format sources
           sources = [
                {
                    "id": doc["id"],
                    "score": doc["score"],
                    "preview": doc["text"][:100] + "...",
                }
                for doc in retrieved_docs[:5]
            ]
            
            response = {
                "answer": answer,
                "sources": sources,
                "code_examples": []  # TODO: Extract code blocks from answer
            }
            
            confidence = sum(doc["score"] for doc in retrieved_docs[:5]) / len(retrieved_docs[:5])
            
        except Exception as e:
            response = {
                "answer": f"Error generating response: {str(e)}",
                "sources": [],
                "code_examples": []
            }
            confidence = 0.0
        
        return AgentOutput(
            result=response,
            metadata={"agent": self.name, "num_sources": len(retrieved_docs)},
            confidence_score=confidence
        )
