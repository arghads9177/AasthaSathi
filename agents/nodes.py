"""
Node implementations for RAG agent workflow.

Each node represents a step in the LangGraph state machine.
"""

import logging
from typing import List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agents.models import AgentState, RetrievedDocument
from agents.prompts import (
    RELEVANCY_CHECK_PROMPT,
    QUERY_REFORMULATION_PROMPT,
    ANSWER_GENERATION_PROMPT,
    FALLBACK_MESSAGE_TEMPLATE,
    CHAT_HISTORY_HEADER
)
from agents.retriever import get_vector_store
from agents.utils import (
    format_chat_history,
    truncate_document_content,
    format_context_from_documents,
    extract_sources
)
from core.config import get_settings, get_provider_manager

logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions - Invoke LLM with provider fallback
# ============================================================================

def _invoke_llm(messages: list, temperature: float = None) -> str:
    """
    Invoke LLM using provider manager with automatic fallback.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        temperature: Optional temperature override
        
    Returns:
        Response text from LLM
    """
    settings = get_settings()
    provider_manager = get_provider_manager()
    
    kwargs = {}
    if temperature is not None:
        kwargs["temperature"] = temperature
    else:
        kwargs["temperature"] = settings.rag_temperature
    
    result = provider_manager.invoke_with_fallback(
        messages=messages,
        **kwargs
    )
    
    return result["response"]


# ============================================================================
# LCEL Chains - Reusable LLM chains with proper structure
# ============================================================================

def get_relevancy_check_chain():
    """
    Create chain for document relevancy checking.
    
    Returns:
        Callable that checks relevancy using provider manager
    """
    prompt_template = ChatPromptTemplate.from_template(RELEVANCY_CHECK_PROMPT)
    
    def chain(inputs):
        # Format prompt
        formatted = prompt_template.format_messages(**inputs)
        
        # Convert to dict messages
        messages = [
            {"role": "system" if msg.type == "system" else "user", "content": msg.content}
            for msg in formatted
        ]
        
        # Invoke with fallback
        return _invoke_llm(messages)
    
    return chain


def get_query_reformulation_chain():
    """
    Create chain for query reformulation.
    
    Returns:
        Callable that reformulates query using provider manager
    """
    prompt_template = ChatPromptTemplate.from_template(QUERY_REFORMULATION_PROMPT)
    
    def chain(inputs):
        # Format prompt
        formatted = prompt_template.format_messages(**inputs)
        
        # Convert to dict messages
        messages = [
            {"role": "system" if msg.type == "system" else "user", "content": msg.content}
            for msg in formatted
        ]
        
        # Invoke with fallback (higher temperature for creativity)
        return _invoke_llm(messages, temperature=0.7)
    
    return chain


def get_answer_generation_chain():
    """
    Create chain for answer generation.
    
    Returns:
        Callable that generates answer using provider manager
    """
    prompt_template = ChatPromptTemplate.from_template(ANSWER_GENERATION_PROMPT)
    
    def chain(inputs):
        # Format prompt
        formatted = prompt_template.format_messages(**inputs)
        
        # Convert to dict messages
        messages = [
            {"role": "system" if msg.type == "system" else "user", "content": msg.content}
            for msg in formatted
        ]
        
        # Invoke with fallback
        return _invoke_llm(messages)
    
    return chain


def retrieve_node(state: AgentState) -> AgentState:
    """
    Retrieve top-5 documents from ChromaDB using vector similarity search.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with retrieved documents
    """
    # Use reformulated query if available, else original
    query = state.get("reformulated_query") or state["user_query"]
    
    logger.info(f"Retrieving documents for query: '{query}'")
    
    try:
        # Get vector store
        vector_store = get_vector_store()
        
        # Retrieve top 5 documents with scores
        results = vector_store.similarity_search_with_score(
            query=query,
            k=5
        )
        
        # Format documents
        retrieved = []
        for doc, score in results:
            retrieved.append(RetrievedDocument(
                content=doc.page_content,
                metadata=doc.metadata,
                source=doc.metadata.get("source_type", "unknown"),
                category=doc.metadata.get("category", "general"),
                relevance_score=float(score),
                is_relevant=None  # Will be determined by LLM
            ))
        
        state["retrieved_documents"] = retrieved
        state["relevant_documents"] = []  # Reset
        state["current_doc_index"] = 0    # Start checking from first doc
        state["execution_path"].append("retrieve")
        
        logger.info(f"✓ Retrieved {len(retrieved)} documents")
        
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        state["retrieved_documents"] = []
        state["relevant_documents"] = []
        state["execution_path"].append("retrieve_error")
    
    return state


def check_relevancy_node(state: AgentState) -> AgentState:
    """
    Check each retrieved document individually for relevancy using GPT-4 with LCEL.
    
    This node checks documents sequentially and stops when relevant ones are found.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with relevancy information
    """
    query = state.get("reformulated_query") or state["user_query"]
    retrieved_docs = state["retrieved_documents"]
    relevant_docs = state.get("relevant_documents", [])
    
    logger.info(f"Checking relevancy of {len(retrieved_docs)} documents individually")
    
    if not retrieved_docs:
        logger.warning("No documents to check")
        state["is_relevant"] = False
        state["execution_path"].append("check_relevancy_no_docs")
        return state
    
    try:
        # Get LCEL chain for relevancy checking
        relevancy_chain = get_relevancy_check_chain()
        
        # Check each document individually
        for idx, doc in enumerate(retrieved_docs, 1):
            logger.info(f"Checking document {idx}/{len(retrieved_docs)} - {doc['source']}:{doc['category']}")
            
            # Truncate content to avoid token limits
            truncated_content = truncate_document_content(doc["content"], max_chars=2000)
            
            # Invoke chain
            result = relevancy_chain({
                "query": query,
                "document_content": truncated_content,
                "source": doc["source"],
                "category": doc["category"]
            })
            
            # Parse result
            result_upper = result.strip().upper()
            if "RELEVANT" in result_upper and "NOT RELEVANT" not in result_upper:
                doc["is_relevant"] = True
                relevant_docs.append(doc)
                logger.info(f"  ✓ Document {idx} marked as RELEVANT")
            else:
                doc["is_relevant"] = False
                logger.info(f"  ✗ Document {idx} marked as NOT RELEVANT")
        
        # Update state
        state["relevant_documents"] = relevant_docs
        state["is_relevant"] = len(relevant_docs) > 0
        state["execution_path"].append("check_relevancy")
        
        logger.info(f"Relevancy check complete: {len(relevant_docs)}/{len(retrieved_docs)} documents relevant")
        
    except Exception as e:
        logger.error(f"Error checking relevancy: {str(e)}")
        state["relevant_documents"] = []
        state["is_relevant"] = False
        state["execution_path"].append("check_relevancy_error")
    
    return state


def reform_query_node(state: AgentState) -> AgentState:
    """
    Reformulate the query for better retrieval using GPT-4 with LCEL.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with reformulated query
    """
    original_query = state["user_query"]
    previous_query = state.get("reformulated_query")
    retry_count = state["retry_count"]
    
    logger.info(f"Reformulating query (attempt {retry_count + 1}/3)")
    
    try:
        # Get LCEL chain for query reformulation
        reformulation_chain = get_query_reformulation_chain()
        
        # Format previous reformulation info
        prev_info = ""
        if previous_query:
            prev_info = f"Previous Reformulated Query: {previous_query}\n"
        
        # Invoke chain
        reformulated = reformulation_chain({
            "original_query": original_query,
            "previous_reformulation": prev_info,
            "retry_count": retry_count + 1
        })
        
        # Remove quotes if present
        reformulated = reformulated.strip().strip('"').strip("'")
        
        state["reformulated_query"] = reformulated
        state["retry_count"] += 1
        state["execution_path"].append("reform_query")
        
        logger.info(f"✓ Query reformulated: '{reformulated}'")
        
    except Exception as e:
        logger.error(f"Error reformulating query: {str(e)}")
        # If reformulation fails, increment retry count anyway
        state["retry_count"] += 1
        state["execution_path"].append("reform_query_error")
    
    return state


def generate_answer_node(state: AgentState) -> AgentState:
    """
    Generate final answer using relevant documents and chat history with LCEL.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with generated answer
    """
    query = state["user_query"]
    relevant_docs = state["relevant_documents"]
    chat_history = state.get("messages", [])
    
    logger.info(f"Generating answer using {len(relevant_docs)} relevant documents")
    
    try:
        # Get LCEL chain for answer generation
        answer_chain = get_answer_generation_chain()
        
        # Format context from relevant documents
        context = format_context_from_documents(relevant_docs, include_metadata=True)
        
        # Format chat history (last 10 messages)
        history_text = ""
        if len(chat_history) > 0:
            formatted_history = format_chat_history(chat_history, max_messages=10)
            history_text = CHAT_HISTORY_HEADER.format(
                formatted_history=formatted_history
            )
        
        # Invoke chain
        answer = answer_chain({
            "chat_history": history_text,
            "query": query,
            "context": context
        })
        
        # Update state
        state["final_answer"] = answer.strip()
        state["sources_used"] = extract_sources(relevant_docs)
        state["execution_path"].append("generate_answer")
        
        # Update chat history
        state["messages"].append(HumanMessage(content=query))
        state["messages"].append(AIMessage(content=answer.strip()))
        
        logger.info("✓ Answer generated successfully")
        
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        error_message = "I apologize, but I encountered an error while generating the answer. Please try asking your question again."
        state["final_answer"] = error_message
        state["execution_path"].append("generate_answer_error")
        
        # Still update chat history
        state["messages"].append(HumanMessage(content=query))
        state["messages"].append(AIMessage(content=error_message))
    
    return state


def fallback_node(state: AgentState) -> AgentState:
    """
    Handle case when no relevant information found after 3 retries.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated agent state with fallback message
    """
    query = state["user_query"]
    
    logger.info("Executing fallback - no relevant information found after retries")
    
    # Generate fallback message
    fallback_message = FALLBACK_MESSAGE_TEMPLATE.format(query=query)
    
    state["final_answer"] = fallback_message
    state["execution_path"].append("fallback")
    
    # Update chat history
    state["messages"].append(HumanMessage(content=query))
    state["messages"].append(AIMessage(content=fallback_message))
    
    logger.info("✓ Fallback message generated")
    
    return state
