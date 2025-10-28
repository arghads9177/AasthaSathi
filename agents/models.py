"""
Data models and state schema for RAG agent workflow.
"""

from typing import TypedDict, List, Optional, Annotated, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class RetrievedDocument(TypedDict):
    """Single retrieved document with metadata."""
    content: str
    metadata: Dict[str, Any]
    source: str
    category: str
    relevance_score: Optional[float]  # From similarity search
    is_relevant: Optional[bool]       # From LLM check


class AgentState(TypedDict):
    """
    State schema for the RAG agent workflow.
    
    This state is passed through all nodes in the LangGraph workflow.
    """
    
    # User interaction
    user_query: str                              # Original user query
    reformulated_query: Optional[str]            # Query after reformulation
    
    # Retrieval (Top 5 documents)
    retrieved_documents: List[RetrievedDocument] # All retrieved docs
    relevant_documents: List[RetrievedDocument]  # Only relevant docs
    
    # Agent processing
    current_doc_index: int                       # For sequential checking
    retry_count: int                             # Number of retry attempts (max 3)
    is_relevant: bool                            # Whether relevant docs found
    
    # Final output
    final_answer: str                            # Generated answer
    
    # Chat history for memory (contextualized conversation)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Metadata
    sources_used: List[str]                      # Document sources used
    execution_path: List[str]                    # Track workflow path for debugging
    session_id: str                              # For memory management
