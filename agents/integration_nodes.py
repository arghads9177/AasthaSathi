"""
Integration nodes for combining API and RAG workflows.

This module contains nodes for routing queries and merging contexts.
"""

import logging
from typing import Dict, Any

from agents.models import AgentState
from agents.router import QueryRouter
from agents.api_agent import APIAgent

logger = logging.getLogger(__name__)


def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Route the query to appropriate datasource(s).
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with routing information
    """
    query = state["user_query"]
    logger.info(f"Routing query: {query}")
    
    try:
        # Use router to classify query
        router = QueryRouter()
        route_result = router.route(query)
        
        logger.info(f"Route decision: {route_result.datasource} - {route_result.reasoning}")
        
        return {
            "datasource": route_result.datasource,
            "routing_reasoning": route_result.reasoning,
            "api_queries": route_result.api_queries,
            "execution_path": state.get("execution_path", []) + ["router"]
        }
    except Exception as e:
        logger.error(f"Error in router node: {str(e)}")
        # Default to RAG on error
        return {
            "datasource": "rag",
            "routing_reasoning": f"Error in routing, defaulting to RAG: {str(e)}",
            "api_queries": [],
            "execution_path": state.get("execution_path", []) + ["router_error"]
        }


def api_call_node(state: AgentState) -> Dict[str, Any]:
    """
    Execute API calls and store results.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with API results
    """
    query = state["user_query"]
    api_queries = state.get("api_queries", [])
    
    logger.info(f"Executing API calls for query: {query}")
    
    try:
        # Use API agent to fetch data
        api_agent = APIAgent()
        result = api_agent.query(query, api_queries)
        
        if result["success"]:
            logger.info("✓ API calls successful")
            return {
                "api_context": result["response"],
                "api_success": True,
                "sources_used": state.get("sources_used", []) + ["API Data"],
                "execution_path": state.get("execution_path", []) + ["api_call"]
            }
        else:
            logger.warning(f"✗ API calls failed: {result.get('error', 'Unknown error')}")
            return {
                "api_context": None,
                "api_success": False,
                "execution_path": state.get("execution_path", []) + ["api_call_failed"]
            }
    except Exception as e:
        logger.error(f"Error in API call node: {str(e)}")
        return {
            "api_context": None,
            "api_success": False,
            "execution_path": state.get("execution_path", []) + ["api_call_error"]
        }


def context_merger_node(state: AgentState) -> Dict[str, Any]:
    """
    Merge API and RAG contexts for hybrid queries.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with merged context
    """
    logger.info("Merging API and RAG contexts")
    
    api_context = state.get("api_context")
    relevant_docs = state.get("relevant_documents", [])
    
    # Build combined context
    merged_context_parts = []
    
    # Add API context if available
    if api_context:
        merged_context_parts.append("=== Real-time Data from API ===")
        merged_context_parts.append(api_context)
        merged_context_parts.append("")
    
    # Add RAG context if available
    if relevant_docs:
        merged_context_parts.append("=== Knowledge Base Information ===")
        for i, doc in enumerate(relevant_docs, 1):
            merged_context_parts.append(f"\nDocument {i}:")
            merged_context_parts.append(doc["content"])
            merged_context_parts.append(f"Source: {doc['source']}")
    
    merged_context = "\n".join(merged_context_parts) if merged_context_parts else None
    
    logger.info(f"Context merged: API={'Yes' if api_context else 'No'}, "
                f"RAG={'Yes' if relevant_docs else 'No'}")
    
    return {
        "execution_path": state.get("execution_path", []) + ["context_merger"]
    }


def api_only_answer_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate answer using only API context.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with final answer
    """
    logger.info("Generating answer from API context only")
    
    api_context = state.get("api_context", "")
    
    # For API-only queries, the API agent already formatted a good response
    # We can use it directly
    return {
        "final_answer": api_context if api_context else "I couldn't retrieve the information from the API.",
        "execution_path": state.get("execution_path", []) + ["api_answer"]
    }

