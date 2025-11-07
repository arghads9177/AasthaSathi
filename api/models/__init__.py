"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
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
    language: Optional[Literal["en", "hi", "bn"]] = Field(
        None,
        description="Preferred language for response (en=English, hi=Hindi, bn=Bengali). If not specified, language will be auto-detected from query.",
        example="en"
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
    detected_language: Optional[str] = Field(
        None,
        description="Auto-detected language from query (en/hi/bn)"
    )
    detection_confidence: Optional[float] = Field(
        None,
        description="Language detection confidence score (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    response_language: Optional[str] = Field(
        None,
        description="Language used for the response (en/hi/bn)"
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
                "query": "ब्याज दर क्या है?",
                "answer": "ब्याज दर 5% प्रति वर्ष है।",
                "datasource": "rag",
                "routing_reasoning": "Query asks about interest rates, knowledge base query",
                "detected_language": "hi",
                "detection_confidence": 1.0,
                "response_language": "hi",
                "sources": ["User Manual - Section 3.2"],
                "metadata": {
                    "execution_path": ["language_detection", "query_translation", "router", "retrieve", "check_relevancy", "generate_answer", "response_translation"],
                    "processing_time_ms": 3245,
                    "retry_count": 0,
                    "api_used": False,
                    "documents_retrieved": 5,
                    "relevant_documents": 3
                },
                "timestamp": "2025-11-06T10:30:00Z"
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
