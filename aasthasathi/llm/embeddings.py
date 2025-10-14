"""
Embeddings Module

Handles embeddings generation for different providers (OpenAI, Gemini).
"""

from typing import List, Optional
import logging
from abc import ABC, abstractmethod

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    try:
        from langchain.embeddings import OpenAIEmbeddings
    except ImportError:
        OpenAIEmbeddings = None

from ..core.config import get_settings


logger = logging.getLogger(__name__)


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        pass
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        pass


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embeddings provider."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        if OpenAIEmbeddings is None:
            raise ImportError("OpenAI embeddings not available. Please install langchain-openai.")
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            model=model
        )
        self.model = model
        logger.info(f"Initialized OpenAI embeddings with model: {model}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        return self.embeddings.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return self.embeddings.embed_query(text)


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Gemini embeddings provider (placeholder - implement based on actual Gemini API)."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-004"):
        self.api_key = api_key
        self.model = model
        # TODO: Initialize actual Gemini embeddings client
        logger.info(f"Initialized Gemini embeddings with model: {model}")
        
        # For now, use a fallback or raise not implemented
        raise NotImplementedError("Gemini embeddings not yet implemented. Please use OpenAI.")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        # TODO: Implement Gemini document embedding
        raise NotImplementedError("Gemini embeddings not yet implemented")
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        # TODO: Implement Gemini query embedding  
        raise NotImplementedError("Gemini embeddings not yet implemented")


def get_embedding_model() -> BaseEmbeddingProvider:
    """Factory function to get the configured embedding model."""
    
    settings = get_settings()
    
    if settings.embedding_provider.lower() == "openai":
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required for OpenAI embeddings")
        
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key,
            model=settings.embedding_model
        )
    
    elif settings.embedding_provider.lower() == "gemini":
        if not settings.gemini_api_key:
            raise ValueError("Gemini API key is required for Gemini embeddings")
        
        return GeminiEmbeddingProvider(
            api_key=settings.gemini_api_key,
            model=settings.embedding_model
        )
    
    else:
        raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")


def test_embeddings():
    """Test embeddings functionality."""
    
    try:
        embedding_model = get_embedding_model()
        
        # Test single query embedding
        test_query = "What is the interest rate for fixed deposits?"
        query_embedding = embedding_model.embed_query(test_query)
        
        print(f"Query embedding dimension: {len(query_embedding)}")
        print(f"First 5 values: {query_embedding[:5]}")
        
        # Test document embeddings
        test_docs = [
            "Fixed deposit schemes offer guaranteed returns with flexible tenure options.",
            "Personal loans are available for eligible members with competitive interest rates.",
            "Savings accounts provide easy access to funds with reasonable interest earnings."
        ]
        
        doc_embeddings = embedding_model.embed_documents(test_docs)
        
        print(f"\nDocument embeddings:")
        print(f"Number of documents: {len(doc_embeddings)}")
        print(f"Embedding dimension: {len(doc_embeddings[0])}")
        
        return True
        
    except Exception as e:
        logger.error(f"Embedding test failed: {e}")
        return False


if __name__ == "__main__":
    test_embeddings()