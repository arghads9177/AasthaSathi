"""Agent service wrapper for API integration."""

import logging
import time
from typing import Dict, Any, Optional, List
from uuid import uuid4

from agents.integrated_agent import get_integrated_agent
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


class AgentService:
    """
    Service layer for integrated agent.
    
    Provides a clean interface between the API and the agent,
    with error handling, timing, and response formatting.
    """
    
    def __init__(self):
        """Initialize agent service."""
        self.agent = None
        self.request_count = 0
        logger.info("AgentService initialized")
    
    def _get_agent(self):
        """Lazy load agent instance."""
        if self.agent is None:
            logger.info("Loading integrated agent...")
            self.agent = get_integrated_agent()
            logger.info("✓ Integrated agent loaded successfully")
        return self.agent
    
    async def process_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        chat_history: Optional[List[BaseMessage]] = None,
        include_sources: bool = True,
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Process a user query through the integrated agent.
        
        Args:
            query: User's question
            session_id: Session ID for conversation continuity
            chat_history: Previous conversation messages
            include_sources: Whether to include source attribution
            include_metadata: Whether to include execution metadata
            
        Returns:
            Dictionary with answer and metadata
            
        Raises:
            Exception: If agent processing fails
        """
        start_time = time.time()
        self.request_count += 1
        
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid4())
        
        logger.info(f"Processing query #{self.request_count}: '{query[:50]}...'")
        logger.info(f"Session ID: {session_id}")
        
        try:
            # Get agent instance
            agent = self._get_agent()
            
            # Process query
            result = agent.query(
                user_query=query,
                session_id=session_id,
                chat_history=chat_history or []
            )
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Build response
            response = {
                "session_id": result.get("session_id", session_id),
                "query": query,
                "answer": result.get("answer", ""),
                "datasource": result.get("datasource", "unknown"),
                "routing_reasoning": result.get("routing_reasoning", ""),
                "sources": result.get("sources", []) if include_sources else [],
                "chat_history": result.get("chat_history", [])
            }
            
            # Add metadata if requested
            if include_metadata:
                response["metadata"] = {
                    "execution_path": result.get("execution_path", []),
                    "processing_time_ms": processing_time_ms,
                    "retry_count": result.get("retry_count", 0),
                    "api_used": result.get("api_used", False),
                    "num_retrieved": result.get("num_retrieved", 0),
                    "num_relevant": result.get("num_relevant", 0)
                }
            
            logger.info(
                f"✓ Query processed successfully - "
                f"Route: {response['datasource']}, "
                f"Time: {processing_time_ms}ms"
            )
            
            return response
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"✗ Error processing query: {str(e)}", exc_info=True)
            
            # Return error response
            return {
                "session_id": session_id,
                "query": query,
                "answer": "I apologize, but I encountered an error processing your query. Please try again.",
                "datasource": "error",
                "routing_reasoning": "",
                "sources": [],
                "chat_history": chat_history or [],
                "metadata": {
                    "error": str(e),
                    "processing_time_ms": processing_time_ms
                } if include_metadata else None
            }


# Global service instance
_agent_service = None


def get_agent_service() -> AgentService:
    """
    Get singleton agent service instance.
    
    Returns:
        AgentService instance
    """
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
