"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User query/question",
        example="What savings schemes are available?"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for conversation continuity (optional)",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    include_sources: bool = Field(
        True,
        description="Include source attribution in response"
    )
    include_metadata: bool = Field(
        True,
        description="Include execution metadata in response"
    )


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    
    session_id: str = Field(
        ...,
        description="Session ID (generated or provided)"
    )
    query: str = Field(
        ...,
        description="User query that was processed"
    )
    answer: str = Field(
        ...,
        description="AI-generated answer"
    )
    datasource: str = Field(
        ...,
        description="Data source used (api, rag, or hybrid)"
    )
    routing_reasoning: Optional[str] = Field(
        None,
        description="Explanation of routing decision"
    )
    sources: List[str] = Field(
        default_factory=list,
        description="List of sources used to generate answer"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Execution metadata (timing, retry count, etc.)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Response timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "query": "What savings schemes are available?",
                "answer": "We offer a Savings Account scheme with 4% interest rate...",
                "datasource": "api",
                "routing_reasoning": "Query asks for current schemes, requires real-time data",
                "sources": ["API Data"],
                "metadata": {
                    "execution_path": ["router", "api_call", "api_answer"],
                    "processing_time_ms": 2341,
                    "retry_count": 0,
                    "api_used": True
                },
                "timestamp": "2025-10-31T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(
        ...,
        description="Error message"
    )
    detail: Optional[str] = Field(
        None,
        description="Detailed error information"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Error timestamp"
    )
