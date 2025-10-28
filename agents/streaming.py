"""
Enhanced node with streaming support using LCEL.

This module provides streaming capabilities for real-time answer generation.
"""

import logging
from typing import AsyncIterator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from agents.models import AgentState
from agents.prompts import ANSWER_GENERATION_PROMPT, CHAT_HISTORY_HEADER
from agents.utils import format_chat_history, format_context_from_documents
from core.config import get_settings

logger = logging.getLogger(__name__)


async def stream_answer_generation(
    query: str,
    relevant_docs: list,
    chat_history: list
) -> AsyncIterator[str]:
    """
    Stream answer generation using LCEL with async support.
    
    This allows for real-time token streaming to the user.
    
    Args:
        query: User query
        relevant_docs: List of relevant documents
        chat_history: Previous conversation messages
        
    Yields:
        Generated tokens in real-time
    """
    settings = get_settings()
    
    logger.info(f"Streaming answer using {len(relevant_docs)} relevant documents")
    
    try:
        # Create LCEL chain with streaming
        prompt = ChatPromptTemplate.from_template(ANSWER_GENERATION_PROMPT)
        llm = ChatOpenAI(
            model=settings.rag_model,
            temperature=settings.rag_temperature,
            api_key=settings.openai_api_key,
            streaming=True  # Enable streaming
        )
        output_parser = StrOutputParser()
        
        # LCEL chain for streaming
        chain = prompt | llm | output_parser
        
        # Format context and history
        context = format_context_from_documents(relevant_docs, include_metadata=True)
        
        history_text = ""
        if len(chat_history) > 0:
            formatted_history = format_chat_history(chat_history, max_messages=10)
            history_text = CHAT_HISTORY_HEADER.format(
                formatted_history=formatted_history
            )
        
        # Stream tokens
        async for token in chain.astream({
            "chat_history": history_text,
            "query": query,
            "context": context
        }):
            yield token
        
        logger.info("✓ Answer streaming completed")
        
    except Exception as e:
        logger.error(f"Error streaming answer: {str(e)}")
        yield "I apologize, but I encountered an error while generating the answer."


def create_streaming_chain():
    """
    Create a streaming-enabled LCEL chain for answer generation.
    
    Returns:
        Runnable chain with streaming support
    """
    settings = get_settings()
    
    prompt = ChatPromptTemplate.from_template(ANSWER_GENERATION_PROMPT)
    llm = ChatOpenAI(
        model=settings.rag_model,
        temperature=settings.rag_temperature,
        api_key=settings.openai_api_key,
        streaming=True
    )
    output_parser = StrOutputParser()
    
    return prompt | llm | output_parser
