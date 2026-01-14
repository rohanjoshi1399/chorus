"""
AWS Bedrock client for LLM and embeddings.

Provides:
- Claude 4.5 Sonnet for text generation
- Titan Embeddings V2 for vector embeddings
"""

import boto3
from typing import List, Optional
from langchain_aws import ChatBedrock, BedrockEmbeddings

from ..config import settings


class BedrockClient:
    """AWS Bedrock client wrapper."""
    
    def __init__(self):
        """Initialize Bedrock client with credentials from settings."""
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        
        # Initialize LangChain Bedrock LLM
        self.llm = ChatBedrock(
            model_id=settings.bedrock_model,
            client=self.bedrock_runtime,
            model_kwargs={
                "temperature": settings.llm_temperature,
                "max_tokens": settings.llm_max_tokens,
            },
        )
        
        # Initialize embeddings
        self.embeddings = BedrockEmbeddings(
            model_id=settings.bedrock_embedding_model,
            client=self.bedrock_runtime,
        )
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Generate text using Claude 4.5 Sonnet.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        # Create a temporary LLM instance if temperature override
        llm = self.llm
        if temperature is not None:
            llm = ChatBedrock(
                model_id=settings.bedrock_model,
                client=self.bedrock_runtime,
                model_kwargs={
                    "temperature": temperature,
                    "max_tokens": settings.llm_max_tokens,
                },
            )
        
        response = await llm.ainvoke(messages)
        return response.content
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            1024-dimensional embedding vector
        """
        embedding = await self.embeddings.aembed_query(text)
        return embedding
    
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = await self.embeddings.aembed_documents(texts)
        return embeddings


# Global Bedrock client instance
bedrock_client = BedrockClient()
