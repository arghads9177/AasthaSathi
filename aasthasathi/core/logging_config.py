"""
Logging Configuration for AasthaSathi

Provides structured logging with audit trail capabilities.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

from .config import get_settings


class AuditLogger:
    """Audit logger for tracking user interactions and API calls."""
    
    def __init__(self, log_file: str = "audit.log"):
        self.logger = logging.getLogger("aasthasathi.audit")
        self.logger.setLevel(logging.INFO)
        
        # Create audit log file handler
        log_path = Path("logs") / log_file
        log_path.parent.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(log_path)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_query(self, user_id: str, query: str, query_type: str, 
                  role: str, session_id: Optional[str] = None):
        """Log a user query."""
        audit_data = {
            "event": "user_query",
            "user_id": user_id,
            "query": query,
            "query_type": query_type,
            "role": role,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(audit_data))
    
    def log_rag_retrieval(self, user_id: str, query: str, 
                         retrieved_docs: list, similarity_scores: list):
        """Log RAG document retrieval."""
        audit_data = {
            "event": "rag_retrieval",
            "user_id": user_id,
            "query": query,
            "documents_retrieved": len(retrieved_docs),
            "sources": [doc.get("source", "unknown") for doc in retrieved_docs],
            "avg_similarity": sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(audit_data))
    
    def log_api_call(self, user_id: str, endpoint: str, 
                     response_status: str, member_id: Optional[str] = None):
        """Log banking API calls."""
        audit_data = {
            "event": "api_call",
            "user_id": user_id,
            "endpoint": endpoint,
            "member_id": member_id,
            "response_status": response_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(audit_data))
    
    def log_response(self, user_id: str, query: str, response: str, 
                     sources_used: list, response_time: float):
        """Log the final response to user."""
        audit_data = {
            "event": "response_generated",
            "user_id": user_id,
            "query": query,
            "response_length": len(response),
            "sources_used": sources_used,
            "response_time_seconds": response_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(audit_data))


def setup_logging():
    """Set up application logging."""
    settings = get_settings()
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    return logging.getLogger("aasthasathi")


# Global audit logger instance
audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Get the audit logger instance."""
    return audit_logger