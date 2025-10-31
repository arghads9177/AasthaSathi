"""
Router agent for query classification.

This module implements a router that classifies user queries to determine
whether they should be handled by:
1. API tools (for real-time data: branches, schemes, accounts, transactions)
2. RAG retrieval (for general banking knowledge from documents)
3. Hybrid approach (combination of both)
"""

from typing import Literal, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import logging

from core.config import Settings, get_provider_manager
from agents.prompts import ROUTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Load settings
settings = Settings()


class RouteQuery(BaseModel):
    """Output schema for query routing."""
    
    datasource: Literal["api", "rag", "hybrid"] = Field(
        ...,
        description="The datasource to use for answering the query"
    )
    reasoning: str = Field(
        ...,
        description="Brief explanation of why this datasource was chosen"
    )
    api_queries: list[str] = Field(
        default_factory=list,
        description="If API is needed, specific queries to make (e.g., 'search branches in Kolkata')"
    )


class QueryRouter:
    """Router for classifying and routing user queries."""
    
    def __init__(self, model_name: str = None, temperature: float = 0):
        """
        Initialize the query router.
        
        Args:
            model_name: LLM model to use (defaults to settings)
            temperature: Temperature for LLM (0 for deterministic)
        """
        self.model_name = model_name or settings.default_model
        self.temperature = temperature
        
        # Get provider manager for automatic fallback
        self.provider_manager = get_provider_manager()
        logger.info(f"Router initialized with provider manager (fallback enabled: {settings.enable_llm_fallback})")
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", ROUTER_SYSTEM_PROMPT),
            ("human", "Query: {query}")
        ])
    
    def route(self, query: str) -> RouteQuery:
        """
        Route a query to the appropriate datasource.
        
        Args:
            query: User query string
            
        Returns:
            RouteQuery object with datasource, reasoning, and api_queries
        """
        # Format prompt
        messages = self.prompt.format_messages(query=query)
        
        # Convert to dict format for provider manager
        messages_dict = [
            {"role": msg.type if msg.type != "human" else "user", "content": msg.content}
            for msg in messages
        ]
        
        # Invoke with fallback support
        result = self.provider_manager.invoke_with_fallback(
            messages=messages_dict,
            temperature=self.temperature,
            response_format=RouteQuery
        )
        
        logger.info(f"Query routed to: {result['response'].datasource} (provider: {result['provider']})")
        
        return result['response']
    
    def route_dict(self, query: str) -> dict:
        """
        Route a query and return result as dictionary.
        
        Args:
            query: User query string
            
        Returns:
            Dictionary with routing information
        """
        result = self.route(query)
        return {
            "datasource": result.datasource,
            "reasoning": result.reasoning,
            "api_queries": result.api_queries
        }


# Convenience function
def route_query(query: str) -> RouteQuery:
    """
    Route a query using the default router.
    
    Args:
        query: User query string
        
    Returns:
        RouteQuery object
    """
    router = QueryRouter()
    return router.route(query)


# Example usage
if __name__ == "__main__":
    # Test the router
    router = QueryRouter()
    
    test_queries = [
        "Where are branches in Kolkata?",
        "How do I open a savings account?",
        "What are the current FD interest rates?",
        "Explain FD schemes and show me the rates",
        "What documents do I need for a loan?",
        "Show me all running loan schemes",
    ]
    
    print("Testing Query Router\n" + "="*60)
    for query in test_queries:
        result = router.route(query)
        print(f"\nQuery: {query}")
        print(f"Route: {result.datasource}")
        print(f"Reasoning: {result.reasoning}")
        if result.api_queries:
            print(f"API Queries: {result.api_queries}")
