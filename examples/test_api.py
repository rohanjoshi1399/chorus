"""
Test the REST API endpoints.

Usage:
    python examples/test_api.py
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_health():
    """Test health endpoint."""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_detailed_health():
    """Test detailed health endpoint."""
    print("🔍 Testing detailed health endpoint...")
    response = requests.get(f"{BASE_URL}/health/detailed")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_chat(query: str):
    """Test chat endpoint."""
    print(f"💬 Testing chat endpoint with query: '{query}'...")
    
    payload = {
        "query": query,
        "session_id": "test-session-123"
    }
    
    response = requests.post(
        f"{BASE_URL}/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📝 Answer: {data['answer'][:200]}...")
        print(f"\n📎 Sources: {len(data['sources'])} documents")
        print(f"🎯 Confidence: {data['metadata']['confidence']:.2f}")
        print(f"📊 Intent: {data['metadata']['query_analysis']['intent']}")
    else:
        print(f"Error: {response.text}")
    
    print()


def test_upload_document():
    """Test document upload endpoint."""
    print("📤 Testing document upload...")
    
    # Create a sample document
    sample_content = """
# Sample Document

This is a test document about retrieval-augmented generation.
RAG systems combine vector search with LLM generation for better accuracy.
"""
    
    files = {
        'files': ('test_rag.txt', sample_content, 'text/plain')
    }
    
    response = requests.post(
        f"{BASE_URL}/docs/upload",
        files=files
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")


def test_search(query: str):
    """Test direct document search."""
    print(f"🔎 Testing document search: '{query}'...")
    
    response = requests.get(
        f"{BASE_URL}/docs/search",
        params={"query": query, "top_k": 3}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Results: {len(data['results'])} documents found")
        for i, result in enumerate(data['results'][:2], 1):
            print(f"\n[{i}] Score: {result['score']:.3f}")
            print(f"    {result['text'][:100]}...")
    
    print()


def main():
    """Run API tests."""
    print("=" * 80)
    print("🧪 Testing Multi-Agent RAG API")
    print("=" * 80)
    print()
    
    # Test health
    test_health()
    test_detailed_health()
    
    # Test document upload
    test_upload_document()
    
    # Test search
    test_search("What is RAG?")
    
    # Test chat
    test_chat("What is retrieval-augmented generation?")
    
    print("=" * 80)
    print("✅ All tests complete!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Make sure the server is running:")
        print("   uvicorn src.api.main:app --reload")

