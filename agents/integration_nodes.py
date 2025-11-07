"""
Integration nodes for combining API and RAG workflows.

This module contains nodes for routing queries and merging contexts,
including multilingual support nodes.
"""

import logging
from typing import Dict, Any

from agents.models import AgentState
from agents.router import QueryRouter
from agents.api_agent import APIAgent
from core.language_detector import LanguageDetector
from core.translation_service import TranslationService

logger = logging.getLogger(__name__)


# ============================================================================
# MULTILINGUAL NODES
# ============================================================================

def language_detection_node(state: AgentState) -> Dict[str, Any]:
    """
    Detect the language of user query and update state.
    
    Args:
        state: Current agent state with query
        
    Returns:
        Updated state with language information
    """
    query = state["user_query"]
    logger.info(f"Detecting language for query: {query[:50]}...")
    
    try:
        detector = LanguageDetector()
        lang_code, confidence = detector.detect_language(query)
        lang_name = detector.get_language_name(lang_code)
        
        logger.info(
            f"Language detected: {lang_name} ({lang_code}) "
            f"with confidence {confidence:.2f}"
        )
        
        return {
            "query_language": lang_code,
            "query_language_confidence": confidence,
            "original_query": query,
            "response_language": lang_code,
            "execution_path": state.get("execution_path", []) + ["language_detection"]
        }
    except Exception as e:
        logger.error(f"Error in language detection: {e}, defaulting to English")
        return {
            "query_language": "en",
            "query_language_confidence": 0.0,
            "original_query": query,
            "response_language": "en",
            "execution_path": state.get("execution_path", []) + ["language_detection_error"]
        }


def query_translation_node(state: AgentState) -> Dict[str, Any]:
    """
    Translate non-English queries to English for processing.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with translated query
    """
    lang = state.get("query_language", "en")
    original_query = state.get("original_query", state["user_query"])
    
    logger.info(f"Processing query translation for language: {lang}")
    
    # Skip translation if already English
    if lang == "en":
        logger.info("Query is in English, skipping translation")
        return {
            "original_query": original_query,
            "translated_query": original_query,  # For English, translated = original
            "user_query": original_query,  # Ensure user_query is set for consistency
            "execution_path": state.get("execution_path", []) + ["query_translation_skipped"]
        }
    
    try:
        # Translate to English for router and retrieval
        translator = TranslationService(enable_cache=True)
        translated = translator.translate_to_english(original_query, lang)
        
        if translated:
            logger.info(f"Query translated: '{original_query[:50]}...' → '{translated[:50]}...'")
            
            # Update user_query for processing (rest of pipeline uses this)
            return {
                "translated_query": translated,
                "user_query": translated,  # Use translated query for processing
                "execution_path": state.get("execution_path", []) + ["query_translation"]
            }
        else:
            logger.warning("Translation failed, using original query")
            return {
                "translated_query": None,
                "execution_path": state.get("execution_path", []) + ["query_translation_failed"]
            }
    except Exception as e:
        logger.error(f"Error in query translation: {e}")
        return {
            "translated_query": None,
            "execution_path": state.get("execution_path", []) + ["query_translation_error"]
        }


def response_translation_node(state: AgentState) -> Dict[str, Any]:
    """
    Translate English responses back to user's language.
    
    Args:
        state: Current agent state with answer
        
    Returns:
        Updated state with translated answer
    """
    response_lang = state.get("response_language", "en")
    answer = state.get("final_answer", "")
    
    logger.info(f"Processing response translation to: {response_lang}")
    
    # Skip translation if already English
    if response_lang == "en":
        logger.info("Response is already in English, skipping translation")
        return {
            "execution_path": state.get("execution_path", []) + ["response_translation_skipped"]
        }
    
    if not answer:
        logger.warning("No answer to translate")
        return {
            "execution_path": state.get("execution_path", []) + ["response_translation_no_answer"]
        }
    
    try:
        # Translate answer to target language
        translator = TranslationService(enable_cache=True)
        translated_answer = translator.translate_from_english(answer, response_lang)
        
        if translated_answer:
            logger.info(f"Answer translated to {response_lang}: '{translated_answer[:50]}...'")
            return {
                "final_answer": translated_answer,
                "execution_path": state.get("execution_path", []) + ["response_translation"]
            }
        else:
            logger.warning("Translation failed, keeping English answer")
            return {
                "execution_path": state.get("execution_path", []) + ["response_translation_failed"]
            }
    except Exception as e:
        logger.error(f"Error in response translation: {e}")
        return {
            "execution_path": state.get("execution_path", []) + ["response_translation_error"]
        }


# ============================================================================
# ROUTING AND CONTEXT NODES
# ============================================================================


def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Route the query to appropriate datasource(s).
    Uses language-aware prompts based on detected language.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with routing information
    """
    query = state["user_query"]
    lang = state.get("query_language", "en")
    
    logger.info(f"Routing query (language: {lang}): {query}")
    
    try:
        # Import multilingual prompts
        from agents.prompts_multilingual import get_prompt
        
        # Get language-specific router prompt
        router_prompt = get_prompt("router_system", lang)
        
        # Use router to classify query (with custom prompt if needed)
        router = QueryRouter()
        
        # Override the system prompt if not English
        if lang != "en" and router_prompt:
            from langchain_core.prompts import ChatPromptTemplate
            router.prompt = ChatPromptTemplate.from_messages([
                ("system", router_prompt),
                ("human", "Query: {query}")
            ])
        
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

