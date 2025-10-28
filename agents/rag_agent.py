"""
LangGraph Agentic RAG workflow definition.

This module defines the state machine for the RAG agent with retry logic.
"""

import logging
from typing import Literal
from uuid import uuid4

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver

from agents.models import AgentState
from agents.nodes import (
    retrieve_node,
    check_relevancy_node,
    reform_query_node,
    generate_answer_node,
    fallback_node
)
from core.config import get_settings

logger = logging.getLogger(__name__)


def route_after_relevancy_check(state: AgentState) -> Literal["generate_answer", "reform_query", "fallback"]:
    """
    Conditional routing after relevancy check.
    
    Decision logic:
    - If relevant documents found → generate answer
    - If retry_count >= 3 → fallback (max retries reached)
    - Otherwise → reform query and retry
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to execute
    """
    settings = get_settings()
    is_relevant = state.get("is_relevant", False)
    retry_count = state.get("retry_count", 0)
    
    if is_relevant:
        logger.info("✓ Relevant documents found - routing to generate_answer")
        return "generate_answer"
    
    if retry_count >= settings.rag_max_retries:
        logger.warning(f"✗ Max retries ({settings.rag_max_retries}) reached - routing to fallback")
        return "fallback"
    
    logger.info(f"→ No relevant docs, retry {retry_count + 1}/{settings.rag_max_retries} - routing to reform_query")
    return "reform_query"


def create_rag_workflow() -> StateGraph:
    """
    Create and compile the RAG agent workflow.
    
    Workflow structure:
    1. retrieve → check_relevancy
    2. check_relevancy → [generate_answer | reform_query | fallback]
    3. reform_query → retrieve (retry loop)
    4. generate_answer → END
    5. fallback → END
    
    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Creating RAG workflow graph")
    
    # Initialize workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("check_relevancy", check_relevancy_node)
    workflow.add_node("reform_query", reform_query_node)
    workflow.add_node("generate_answer", generate_answer_node)
    workflow.add_node("fallback", fallback_node)
    
    # Set entry point
    workflow.set_entry_point("retrieve")
    
    # Add edges
    workflow.add_edge("retrieve", "check_relevancy")
    workflow.add_conditional_edges(
        "check_relevancy",
        route_after_relevancy_check,
        {
            "generate_answer": "generate_answer",
            "reform_query": "reform_query",
            "fallback": "fallback"
        }
    )
    workflow.add_edge("reform_query", "retrieve")  # Retry loop
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("fallback", END)
    
    # Compile with memory checkpointing
    memory = MemorySaver()
    compiled_workflow = workflow.compile(checkpointer=memory)
    
    logger.info("✓ RAG workflow compiled successfully")
    
    return compiled_workflow


class RAGAgent:
    """
    Agentic RAG system for Aastha Co-operative Credit Society.
    
    Features:
    - Multi-step retrieval with retry logic
    - LLM-based relevancy checking
    - Query reformulation for improved results
    - Memory-enabled conversation tracking
    """
    
    def __init__(self):
        """Initialize RAG agent with compiled workflow."""
        self.workflow = create_rag_workflow()
        logger.info("RAG Agent initialized")
    
    def query(
        self,
        user_query: str,
        session_id: str = None,
        chat_history: list[BaseMessage] = None
    ) -> dict:
        """
        Execute RAG workflow for a user query.
        
        Args:
            user_query: User's question
            session_id: Session identifier for memory (default: new UUID)
            chat_history: Previous conversation messages (optional)
            
        Returns:
            Dictionary with answer, sources, and execution details
        """
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid4())
        
        logger.info(f"Processing query for session {session_id}: '{user_query}'")
        
        # Initialize state
        initial_state = AgentState(
            user_query=user_query,
            reformulated_query=None,
            retrieved_documents=[],
            relevant_documents=[],
            retry_count=0,
            is_relevant=False,
            final_answer=None,
            messages=chat_history or [],
            sources_used=[],
            execution_path=[],
            session_id=session_id
        )
        
        # Execute workflow
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            final_state = self.workflow.invoke(initial_state, config)
            
            # Extract results
            result = {
                "answer": final_state["final_answer"],
                "sources": final_state["sources_used"],
                "execution_path": final_state["execution_path"],
                "retry_count": final_state["retry_count"],
                "session_id": session_id,
                "num_retrieved": len(final_state["retrieved_documents"]),
                "num_relevant": len(final_state["relevant_documents"]),
                "chat_history": final_state["messages"]
            }
            
            logger.info(
                f"✓ Query completed - "
                f"Path: {' → '.join(result['execution_path'])}, "
                f"Retries: {result['retry_count']}, "
                f"Relevant: {result['num_relevant']}/{result['num_retrieved']}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return {
                "answer": "I apologize, but I encountered an error processing your query. Please try again.",
                "sources": [],
                "execution_path": ["error"],
                "retry_count": 0,
                "session_id": session_id,
                "num_retrieved": 0,
                "num_relevant": 0,
                "error": str(e)
            }
    
    def stream_query(
        self,
        user_query: str,
        session_id: str = None,
        chat_history: list[BaseMessage] = None
    ):
        """
        Stream RAG workflow execution with intermediate states.
        
        Args:
            user_query: User's question
            session_id: Session identifier for memory (default: new UUID)
            chat_history: Previous conversation messages (optional)
            
        Yields:
            State updates as workflow progresses
        """
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid4())
        
        logger.info(f"Streaming query for session {session_id}: '{user_query}'")
        
        # Initialize state
        initial_state = AgentState(
            user_query=user_query,
            reformulated_query=None,
            retrieved_documents=[],
            relevant_documents=[],
            retry_count=0,
            is_relevant=False,
            final_answer=None,
            messages=chat_history or [],
            sources_used=[],
            execution_path=[],
            session_id=session_id
        )
        
        # Stream workflow execution
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            for state in self.workflow.stream(initial_state, config):
                yield state
        except Exception as e:
            logger.error(f"Error streaming workflow: {str(e)}")
            yield {"error": str(e)}


# Global agent instance
_rag_agent = None


def get_rag_agent() -> RAGAgent:
    """
    Get singleton RAG agent instance.
    
    Returns:
        RAGAgent instance
    """
    global _rag_agent
    if _rag_agent is None:
        _rag_agent = RAGAgent()
    return _rag_agent


def reset_rag_agent():
    """Reset the global RAG agent instance (for testing)."""
    global _rag_agent
    _rag_agent = None
    logger.info("RAG Agent reset")
