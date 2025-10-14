"""
Common Data Models for AasthaSathi

Pydantic models for data validation and serialization.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles with different access levels."""
    ADMIN = "admin"
    EMPLOYEE = "employee" 
    AGENT = "agent"
    PUBLIC = "public"


class QueryType(str, Enum):
    """Types of queries the system can handle."""
    POLICY = "policy"           # RAG-only queries about policies/schemes
    ACCOUNT = "account"         # API-only queries about member accounts
    HYBRID = "hybrid"           # Combined RAG + API queries


class DocumentSource(str, Enum):
    """Sources of documents in the knowledge base."""
    WEBSITE = "website"
    PDF_MANUAL = "pdf_manual"
    FAQ = "faq"
    POLICY_DOC = "policy_doc"


class User(BaseModel):
    """User model for authentication and authorization."""
    user_id: str
    username: str
    role: UserRole
    permissions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class Document(BaseModel):
    """Document model for knowledge base entries."""
    doc_id: str
    title: str
    content: str
    source: DocumentSource
    url: Optional[str] = None
    page_number: Optional[int] = None
    section: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentChunk(BaseModel):
    """Chunked document for vector storage."""
    chunk_id: str
    doc_id: str
    content: str
    chunk_index: int
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None


class Query(BaseModel):
    """User query model."""
    query_id: str = Field(default_factory=lambda: f"q_{datetime.utcnow().timestamp()}")
    user_id: str
    text: str
    query_type: Optional[QueryType] = None
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RetrievedDocument(BaseModel):
    """Document retrieved from vector search."""
    doc_id: str
    content: str
    similarity_score: float
    source: DocumentSource
    metadata: Dict[str, Any] = {}


class APIResponse(BaseModel):
    """Response from banking API calls."""
    endpoint: str
    status_code: int
    data: Dict[str, Any] = {}
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    response_id: str = Field(default_factory=lambda: f"r_{datetime.utcnow().timestamp()}")
    query_id: str
    text: str
    sources: List[str] = []
    query_type: QueryType
    confidence: float = Field(ge=0.0, le=1.0)
    response_time: float  # seconds
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MemberAccount(BaseModel):
    """Member account information from banking API."""
    member_id: str
    name: str
    account_number: str
    balance: float
    schemes: List[Dict[str, Any]] = []
    status: str
    last_transaction: Optional[datetime] = None


class PolicyInfo(BaseModel):
    """Policy information from knowledge base."""
    policy_id: str
    title: str
    description: str
    eligibility: List[str] = []
    benefits: List[str] = []
    withdrawal_rules: str
    interest_rate: Optional[float] = None
    minimum_amount: Optional[float] = None


class AuditLog(BaseModel):
    """Audit log entry."""
    log_id: str = Field(default_factory=lambda: f"log_{datetime.utcnow().timestamp()}")
    event: str
    user_id: str
    details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SystemHealth(BaseModel):
    """System health status."""
    status: Literal["healthy", "degraded", "unhealthy"]
    vector_db_status: bool
    api_status: bool
    llm_status: bool
    last_check: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = {}