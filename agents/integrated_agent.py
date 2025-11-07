"""
Integrated LangGraph workflow with Router, API, and RAG.

This module defines the unified state machine that combines:
- Query routing (API vs RAG vs Hybrid)
- API agent for real-time data
- RAG agent for knowledge base
- Context merging for hybrid queries
- Multilingual support (English, Hindi, Bengali)
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
from agents.integration_nodes import (
    language_detection_node,
    query_translation_node,
    response_translation_node,
    router_node,
    api_call_node,
    context_merger_node,
    api_only_answer_node
)
from core.config import get_settings

logger = logging.getLogger(__name__)


def route_after_router(state: AgentState) -> Literal["api_call", "retrieve", "api_and_retrieve"]:
    """
    Route based on router decision.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to execute based on datasource
    """
    datasource = state.get("datasource", "rag")
    
    if datasource == "api":
        logger.info("→ Routing to API only")
        return "api_call"
    elif datasource == "rag":
        logger.info("→ Routing to RAG only")
        return "retrieve"
    else:  # hybrid
        logger.info("→ Routing to API + RAG (hybrid)")
        return "api_and_retrieve"


def route_after_api_call(state: AgentState) -> Literal["api_answer", "fallback"]:
    """
    Route after API call for API-only queries.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node based on API success
    """
    api_success = state.get("api_success", False)
    
    if api_success:
        logger.info("✓ API successful - routing to api_answer")
        return "api_answer"
    else:
        logger.warning("✗ API failed - routing to fallback")
        return "fallback"


def route_after_api_and_retrieve(state: AgentState) -> Literal["context_merger", "retrieve"]:
    """
    Route after parallel API and RAG retrieval for hybrid queries.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to execute
    """
    api_success = state.get("api_success", False)
    has_docs = len(state.get("retrieved_documents", [])) > 0
    
    if api_success or has_docs:
        logger.info("→ Have API or RAG data - routing to context_merger")
        return "context_merger"
    else:
        logger.info("→ No data from either source - routing to retrieve for retry")
        return "retrieve"


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


def route_after_answer(state: AgentState) -> str:
    """
    Route after answer generation to determine if translation is needed.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node name or "__end__" for END
    """
    response_language = state.get("response_language", "en")
    
    if response_language and response_language != "en":
        logger.info(f"→ Translating response to {response_language}")
        return "response_translation"
    else:
        logger.info("✓ Response in English - no translation needed")
        return "__end__"


def create_integrated_workflow() -> StateGraph:
    """
    Create and compile the integrated workflow with Multilingual + Router + API + RAG.
    
    Workflow structure:
    0. Multilingual processing: language_detection → query_translation
    1. router → [api_call | retrieve | api_and_retrieve]
    2. API-only path: api_call → api_answer → response_translation → END
    3. RAG-only path: retrieve → check_relevancy → [generate_answer | reform_query | fallback] → response_translation → END
    4. Hybrid path: api_and_retrieve → context_merger → check_relevancy → generate_answer → response_translation → END
    
    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Creating integrated multilingual workflow graph")
    
    # Initialize workflow
    workflow = StateGraph(AgentState)
    
    # Add language processing nodes (Phase 2 - Multilingual)
    workflow.add_node("language_detection", language_detection_node)
    workflow.add_node("query_translation", query_translation_node)
    workflow.add_node("response_translation", response_translation_node)
    
    # Add all nodes
    # Routing and API nodes
    workflow.add_node("router", router_node)
    workflow.add_node("api_call", api_call_node)
    workflow.add_node("api_and_retrieve", api_and_retrieve_hybrid_node)
    workflow.add_node("context_merger", context_merger_node)
    workflow.add_node("api_answer", api_only_answer_node)
    
    # RAG nodes
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("check_relevancy", check_relevancy_node)
    workflow.add_node("reform_query", reform_query_node)
    workflow.add_node("generate_answer", generate_answer_node)
    workflow.add_node("fallback", fallback_node)
    
    # Set entry point - start with language detection
    workflow.set_entry_point("language_detection")
    
    # Language processing flow
    workflow.add_edge("language_detection", "query_translation")
    workflow.add_edge("query_translation", "router")
    
    # Add edges from router
    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "api_call": "api_call",
            "retrieve": "retrieve",
            "api_and_retrieve": "api_and_retrieve"
        }
    )
    
    # API-only path
    workflow.add_conditional_edges(
        "api_call",
        route_after_api_call,
        {
            "api_answer": "api_answer",
            "fallback": "fallback"
        }
    )
    workflow.add_conditional_edges(
        "api_answer",
        route_after_answer,
        {
            "response_translation": "response_translation",
            "__end__": END
        }
    )
    
    # Hybrid path
    workflow.add_edge("api_and_retrieve", "context_merger")
    workflow.add_edge("context_merger", "check_relevancy")
    
    # RAG path (shared with hybrid after context merger)
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
    
    # All answer/fallback nodes route to translation check
    workflow.add_conditional_edges(
        "generate_answer",
        route_after_answer,
        {
            "response_translation": "response_translation",
            "__end__": END
        }
    )
    workflow.add_conditional_edges(
        "fallback",
        route_after_answer,
        {
            "response_translation": "response_translation",
            "__end__": END
        }
    )
    
    # Response translation leads to END
    workflow.add_edge("response_translation", END)
    
    # Compile with memory checkpointing
    memory = MemorySaver()
    compiled_workflow = workflow.compile(checkpointer=memory)
    
    logger.info("✓ Integrated multilingual workflow compiled successfully")
    
    return compiled_workflow


def api_and_retrieve_hybrid_node(state: AgentState) -> dict:
    """
    Execute both API call and RAG retrieval in parallel for hybrid queries.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with both API and RAG results
    """
    logger.info("Executing hybrid: API + RAG retrieval")
    
    # Execute API call
    api_result = api_call_node(state)
    
    # Execute RAG retrieval
    rag_result = retrieve_node(state)
    
    # Merge results
    merged_state = {
        "api_context": api_result.get("api_context"),
        "api_success": api_result.get("api_success", False),
        "retrieved_documents": rag_result.get("retrieved_documents", []),
        "sources_used": state.get("sources_used", []) + api_result.get("sources_used", []),
        "execution_path": state.get("execution_path", []) + ["hybrid_fetch"]
    }
    
    logger.info(f"Hybrid fetch complete: API={'✓' if merged_state['api_success'] else '✗'}, "
                f"RAG docs={len(merged_state['retrieved_documents'])}")
    
    return merged_state


class IntegratedAgent:
    """
    Integrated AI agent for Aastha Co-operative Credit Society.
    
    Combines:
    - Query routing for intelligent data source selection
    - API calls for real-time banking data
    - RAG retrieval for knowledge base information
    - Context merging for comprehensive answers
    """
    
    def __init__(self):
        """Initialize integrated agent with compiled workflow."""
        self.workflow = create_integrated_workflow()
        logger.info("Integrated Agent initialized")
    
    def query(
        self,
        user_query: str,
        session_id: str = None,
        chat_history: list[BaseMessage] = None,
        language: str = None
    ) -> dict:
        """
        Execute integrated workflow for a user query.
        
        Args:
            user_query: User's question
            session_id: Session identifier for memory (default: new UUID)
            chat_history: Previous conversation messages (optional)
            language: Preferred language for response (en/hi/bn), auto-detected if None
            
        Returns:
            Dictionary with answer, sources, routing info, language metadata, and execution details
        """
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid4())
        
        logger.info(f"Processing query for session {session_id}: '{user_query}'")
        if language:
            logger.info(f"Preferred language: {language}")
        
        # Initialize state
        initial_state = AgentState(
            user_query=user_query,
            reformulated_query=None,
            datasource=None,
            routing_reasoning=None,
            api_queries=None,
            api_context=None,
            api_success=None,
            retrieved_documents=[],
            relevant_documents=[],
            current_doc_index=0,
            retry_count=0,
            is_relevant=False,
            final_answer=None,
            messages=chat_history or [],
            sources_used=[],
            execution_path=[],
            session_id=session_id,
            # Phase 4 - Set response language if specified (skips detection if provided)
            response_language=language if language else None
        )
        
        # Execute workflow
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            final_state = self.workflow.invoke(initial_state, config)
            
            # Extract results
            result = {
                "answer": final_state["final_answer"],
                "datasource": final_state.get("datasource", "unknown"),
                "routing_reasoning": final_state.get("routing_reasoning", ""),
                "sources": final_state["sources_used"],
                "execution_path": final_state["execution_path"],
                "retry_count": final_state.get("retry_count", 0),
                "session_id": session_id,
                "num_retrieved": len(final_state.get("retrieved_documents", [])),
                "num_relevant": len(final_state.get("relevant_documents", [])),
                "api_used": final_state.get("api_success", False),
                "chat_history": final_state["messages"],
                # Phase 4 - Include language metadata
                "query_language": final_state.get("query_language"),
                "query_language_confidence": final_state.get("query_language_confidence"),
                "response_language": final_state.get("response_language")
            }
            
            logger.info(
                f"✓ Query completed - "
                f"Route: {result['datasource']}, "
                f"Lang: {result.get('query_language', 'unknown')}, "
                f"Path: {' → '.join(result['execution_path'][:5])}{'...' if len(result['execution_path']) > 5 else ''}, "
                f"API: {'Yes' if result['api_used'] else 'No'}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return {
                "answer": "I apologize, but I encountered an error processing your query. Please try again.",
                "datasource": "error",
                "routing_reasoning": "",
                "sources": [],
                "execution_path": ["error"],
                "retry_count": 0,
                "session_id": session_id,
                "num_retrieved": 0,
                "num_relevant": 0,
                "api_used": False,
                "error": str(e)
            }


# Global agent instance
_integrated_agent = None


def get_integrated_agent() -> IntegratedAgent:
    """
    Get singleton integrated agent instance.
    
    Returns:
        IntegratedAgent instance
    """
    global _integrated_agent
    if _integrated_agent is None:
        _integrated_agent = IntegratedAgent()
    return _integrated_agent


def reset_integrated_agent():
    """Reset the global integrated agent instance (for testing)."""
    global _integrated_agent
    _integrated_agent = None
    logger.info("Integrated Agent reset")

