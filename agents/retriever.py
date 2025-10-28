"""
ChromaDB Retriever for RAG agent.

Handles vector store initialization and document retrieval.
"""

import logging
from pathlib import Path
from typing import Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_settings
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

# Global vector store instance (singleton pattern)
_vector_store: Optional[Chroma] = None


def get_vector_store() -> Chroma:
    """
    Get or initialize the ChromaDB vector store.
    
    Returns:
        Chroma: Initialized vector store instance
    """
    global _vector_store
    
    if _vector_store is None:
        logger.info("Initializing ChromaDB vector store...")
        settings = get_settings()
        
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
            dimensions=settings.embedding_dimension
        )
        
        # Initialize Chroma
        _vector_store = Chroma(
            collection_name=settings.chroma_collection_name,
            embedding_function=embeddings,
            persist_directory=settings.vector_db_path
        )
        
        logger.info(f"Vector store initialized: {settings.chroma_collection_name}")
    
    return _vector_store


def reset_vector_store():
    """Reset the global vector store instance (useful for testing)."""
    global _vector_store
    _vector_store = None
    logger.info("Vector store instance reset")
