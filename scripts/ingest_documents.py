"""
Simple document ingestion script.

Processes text files and adds them to the vector database.
"""

import asyncio
import os
from pathlib import Path
from typing import List

from src.retrieval import vector_store


async def ingest_text_file(file_path: Path) -> str:
    """
    Ingest a single text file.
    
    Args:
        file_path: Path to text file
        
    Returns:
        Document ID
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Create chunks (simple split for MVP)
    chunks = [content[i:i+1000] for i in range(0, len(content), 800)]  # 200 char overlap
    
    # Add metadata
    metadatas = [
        {
            "source": str(file_path),
            "filename": file_path.name,
            "chunk_index": i,
            "total_chunks": len(chunks),
        }
        for i in range(len(chunks))
    ]
    
    # Ingest to vector store
    ids = await vector_store.add_documents(texts=chunks, metadatas=metadatas)
    
    print(f"✅ Ingested {file_path.name}: {len(chunks)} chunks")
    return ids


async def ingest_directory(directory: str):
    """
    Ingest all text files in a directory.
    
    Args:
        directory: Path to directory containing text files
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"❌ Directory not found: {directory}")
        return
    
    # Find all text files
    text_files = list(dir_path.glob("**/*.txt")) + list(dir_path.glob("**/*.md"))
    
    if not text_files:
        print(f"❌ No .txt or .md files found in {directory}")
        return
    
    print(f"📁 Found {len(text_files)} files to ingest\n")
    
    # Ingest each file
    for file_path in text_files:
        await ingest_text_file(file_path)
    
    # Get collection stats
    info = vector_store.get_collection_info()
    print(f"\n✅ Ingestion complete!")
    print(f"📊 Collection stats: {info['points_count']} documents")


async def main():
    """Main ingestion function."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.ingest_documents <directory>")
        print("Example: python -m scripts.ingest_documents ./data/docs")
        sys.exit(1)
    
    directory = sys.argv[1]
    await ingest_directory(directory)


if __name__ == "__main__":
    asyncio.run(main())
