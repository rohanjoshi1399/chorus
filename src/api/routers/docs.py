"""Document upload and management endpoints."""

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
import tempfile
from pathlib import Path

from ...retrieval import vector_store


router = APIRouter()


class UploadResponse(BaseModel):
    """Upload response model."""
    uploaded: int
    total_chunks: int
    status: str
    document_ids: List[str]


@router.post("/docs/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload documents for ingestion into vector database.
    
    Supported formats: TXT, MD
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    all_ids = []
    total_chunks = 0
    
    for file in files:
        # Validate file type
        if not file.filename.endswith(('.txt', '.md')):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}. Only .txt and .md files are supported."
            )
        
        try:
            # Read file content
            content = await file.read()
            text = content.decode('utf-8')
            
            # Create chunks (simple split for MVP)
            chunk_size = 1000
            overlap = 200
            chunks = [
                text[i:i+chunk_size]
                for i in range(0, len(text), chunk_size - overlap)
            ]
            
            # Prepare metadata
            metadatas = [
                {
                    "filename": file.filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }
                for i in range(len(chunks))
            ]
            
            # Ingest to vector store
            ids = await vector_store.add_documents(
                texts=chunks,
                metadatas=metadatas,
            )
            
            all_ids.extend(ids)
            total_chunks += len(chunks)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing {file.filename}: {str(e)}"
            )
    
    return UploadResponse(
        uploaded=len(files),
        total_chunks=total_chunks,
        status="completed",
        document_ids=all_ids,
    )


@router.get("/docs/search")
async def search_documents(query: str, top_k: int = 5):
    """Direct vector search (bypasses agents)."""
    try:
        results = await vector_store.similarity_search(
            query=query,
            top_k=top_k,
        )
        return {"query": query, "results": results}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching documents: {str(e)}"
        )
