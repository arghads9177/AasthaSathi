"""
Groq LLM provider implementation.

Wraps Groq's ultra-fast LPU-powered models with error handling and health monitoring.
"""

import logging
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from core.llm_providers.base import (
    BaseLLMProvider,
    QuotaExceededError,
    RateLimitError,
    ProviderUnavailableError,
    ProviderError
)

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """Groq provider using langchain-groq."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-70b-versatile",
        priority: int = 2,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ):
        """
        Initialize Groq provider.
        
        Args:
            api_key: Groq API key
            model: Model name (e.g., "llama-3.1-70b-versatile", "llama-3.1-405b-reasoning")
            priority: Provider priority (2=fallback)
            temperature: Model temperature
            max_tokens: Maximum tokens in response
        """
        super().__init__(
            api_key=api_key,
            model=model,
            name="groq",
            priority=priority,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Initialize LangChain ChatGroq
        self.llm = ChatGroq(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        logger.info(f"Groq provider initialized with model: {model}")
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Invoke the Groq LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Response text
            
        Raises:
            ProviderError: On invocation failure
        """
        try:
            self.record_request()
            
            # Use configured LLM
            llm = self.llm
            
            # Convert to LangChain messages
            lc_messages = self._convert_messages(messages)
            
            # Invoke LLM
            response = llm.invoke(lc_messages)
            
            self.record_success()
            return response.content
            
        except Exception as e:
            self.record_error(e)
            self.handle_error(e)
    
    def invoke_with_tools(self, messages: List[Dict[str, str]], tools: list, **kwargs) -> str:
        """
        Invoke LLM with tool calling support.
        
        Args:
            messages: List of message dicts
            tools: List of tools to bind
            **kwargs: Additional parameters
            
        Returns:
            Response text or tool calls
            
        Raises:
            ProviderError: On invocation failure
        """
        try:
            self.record_request()
            
            # Use configured LLM and bind tools
            llm = self.llm
            llm_with_tools = llm.bind_tools(tools)
            
            # Convert messages
            lc_messages = self._convert_messages(messages)
            
            # Invoke with tools
            response = llm_with_tools.invoke(lc_messages)
            
            self.record_success()
            return response
            
        except Exception as e:
            self.record_error(e)
            self.handle_error(e)
    
    def get_structured_output(
        self,
        messages: List[Dict[str, str]],
        response_format,
        **kwargs
    ):
        """
        Get structured output using Groq's JSON mode.
        
        Args:
            messages: List of message dicts
            response_format: Pydantic model for response structure
            **kwargs: Additional parameters
            
        Returns:
            Structured response matching the Pydantic model
            
        Raises:
            ProviderError: On invocation failure
        """
        try:
            self.record_request()
            
            # Use configured LLM with structured output
            llm = self.llm
            structured_llm = llm.with_structured_output(response_format)
            
            # Convert messages
            lc_messages = self._convert_messages(messages)
            
            # Invoke with structured output
            response = structured_llm.invoke(lc_messages)
            
            self.record_success()
            return response
            
        except Exception as e:
            self.record_error(e)
            self.handle_error(e)
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> list:
        """Convert dict messages to LangChain message objects."""
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role in ("user", "human"):
                lc_messages.append(HumanMessage(content=content))
            elif role in ("assistant", "ai"):
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))
        
        return lc_messages
    
    def get_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings (Groq doesn't support embeddings).
        
        Args:
            text: Text to embed
            
        Returns:
            Empty list (not supported)
        """
        logger.warning("Groq does not support embeddings, returning empty list")
        return []
    
    def handle_error(self, error: Exception):
        """
        Handle and classify errors from Groq API.
        
        Args:
            error: The exception that occurred
            
        Raises:
            QuotaExceededError: If quota is exceeded
            RateLimitError: If rate limit is hit
            ProviderUnavailableError: If service is unavailable
            ProviderError: For other errors
        """
        error_str = str(error).lower()
        
        # Check for rate limiting (Groq has rate limits)
        if "rate" in error_str and "limit" in error_str:
            logger.error(f"Groq: Rate limit - {error}")
            self.open_circuit_breaker(cooldown_seconds=60)  # 1 minute
            raise RateLimitError(f"Groq rate limit: {error}")
        
        # Check for quota exceeded
        if "quota" in error_str or "429" in error_str:
            logger.error(f"Groq: Quota exceeded - {error}")
            self.open_circuit_breaker(cooldown_seconds=180)  # 3 minutes
            raise QuotaExceededError(f"Groq quota exceeded: {error}")
        
        # Check for service unavailable
        if "503" in error_str or "unavailable" in error_str or "timeout" in error_str:
            logger.error(f"Groq: Service unavailable - {error}")
            raise ProviderUnavailableError(f"Groq unavailable: {error}")
        
        # Generic error
        logger.error(f"Groq: Error - {error}")
        raise ProviderError(f"Groq error: {error}")
