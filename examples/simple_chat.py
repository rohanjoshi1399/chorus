"""
Simple chat example demonstrating the MVP 3-agent system.

Usage:
    python examples/simple_chat.py "What is retrieval-augmented generation?"
"""

import asyncio
import sys

from src.agents.base_agent import AgentInput
from src.agents.query_analyzer import QueryAnalyzerAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.synthesis_agent import SynthesisAgent


async def run_chat(query: str):
    """
    Run a simple 3-agent RAG pipeline.
    
    Flow: Query Analyzer → Retrieval → Synthesis
    """
    print(f"🔍 Query: {query}\n")
    
    # Step 1: Query Analysis
    print("📊 Step 1: Analyzing query...")
    query_analyzer = QueryAnalyzerAgent()
    analysis_input = AgentInput(query=query)
    analysis_output = await query_analyzer.run(analysis_input)
    
    print(f"   Intent: {analysis_output.result.get('intent')}")
    print(f"   Complexity: {analysis_output.result.get('complexity')}")
    print(f"   Entities: {analysis_output.result.get('entities')}\n")
    
    # Step 2: Retrieval
    print("📚 Step 2: Retrieving relevant documents...")
    retrieval_agent = RetrievalAgent()
    retrieval_input = AgentInput(
        query=query,
        context={"top_k": 5}
    )
    retrieval_output = await retrieval_agent.run(retrieval_input)
    
    docs = retrieval_output.result.get("documents", [])
    print(f"   Found {len(docs)} relevant documents")
    if docs:
        print(f"   Average relevance score: {retrieval_output.result.get('average_score', 0):.2f}\n")
    else:
        print("   ⚠️ No documents found! Make sure you've ingested documents first.\n")
        return
    
    # Step 3: Synthesis
    print("✨ Step 3: Generating response...")
    synthesis_agent = SynthesisAgent()
    synthesis_input = AgentInput(
        query=query,
        context={"retrieved_documents": docs}
    )
    synthesis_output = await synthesis_agent.run(synthesis_input)
    
    # Display response
    response = synthesis_output.result
    print("\n" + "="*80)
    print("📝 ANSWER:")
    print("="*80)
    print(response.get("answer", "No answer generated"))
    print("\n" + "="*80)
    print(f"📎 SOURCES: {len(response.get('sources', []))} documents")
    print("="*80)
    
    for i, source in enumerate(response.get("sources", [])[:3], 1):
        print(f"\n[{i}] Score: {source.get('score', 0):.3f}")
        print(f"    {source.get('preview', '')}")
    
    print(f"\n✅ Confidence: {synthesis_output.confidence_score:.2f}")


async def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python examples/simple_chat.py '<your question>'")
        print("Example: python examples/simple_chat.py 'What is RAG?'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    await run_chat(query)


if __name__ == "__main__":
    asyncio.run(main())
