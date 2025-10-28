"""
Utility functions for RAG agent workflow.
"""

from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


def format_chat_history(messages: List[BaseMessage], max_messages: int = 10) -> str:
    """
    Format chat history for prompt inclusion.
    
    Args:
        messages: List of chat messages
        max_messages: Maximum number of recent messages to include
        
    Returns:
        Formatted chat history string
    """
    if not messages or len(messages) == 0:
        return ""
    
    # Get recent messages
    recent_messages = messages[-max_messages:]
    
    formatted = []
    for msg in recent_messages:
        if isinstance(msg, HumanMessage):
            formatted.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            formatted.append(f"Assistant: {msg.content}")
    
    return "\n".join(formatted)


def truncate_document_content(content: str, max_chars: int = 2000) -> str:
    """
    Truncate document content to fit within token limits.
    
    Args:
        content: Document content to truncate
        max_chars: Maximum number of characters
        
    Returns:
        Truncated content
    """
    if len(content) <= max_chars:
        return content
    
    # Truncate and add ellipsis
    return content[:max_chars] + "\n\n[Content truncated for brevity...]"


def format_context_from_documents(documents: List[dict], include_metadata: bool = True) -> str:
    """
    Format retrieved documents into context string for LLM.
    
    Args:
        documents: List of retrieved documents
        include_metadata: Whether to include metadata in formatting
        
    Returns:
        Formatted context string
    """
    context_parts = []
    
    for i, doc in enumerate(documents, 1):
        context_parts.append(f"[Document {i}]")
        
        if include_metadata:
            source = doc.get("source", "unknown")
            category = doc.get("category", "general")
            context_parts.append(f"Source: {source} | Category: {category}")
        
        context_parts.append(doc["content"])
        context_parts.append("")  # Empty line between documents
    
    return "\n".join(context_parts)


def extract_sources(documents: List[dict]) -> List[str]:
    """
    Extract source information from documents.
    
    Args:
        documents: List of documents with metadata
        
    Returns:
        List of source identifiers
    """
    sources = []
    for doc in documents:
        metadata = doc.get("metadata", {})
        
        # Prioritize different source identifiers
        if "url" in metadata:
            sources.append(metadata["url"])
        elif "section_title" in metadata:
            sources.append(f"User Manual - {metadata['section_title']}")
        elif "source" in doc:
            sources.append(doc["source"])
        else:
            sources.append("unknown")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_sources = []
    for source in sources:
        if source not in seen:
            seen.add(source)
            unique_sources.append(source)
    
    return unique_sources
