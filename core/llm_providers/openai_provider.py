"""
OpenAI LLM provider implementation.

Wraps OpenAI's ChatGPT models with error handling and health monitoring.
"""

import logging
from typing import List, Dict
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from core.llm_providers.base import (
    BaseLLMProvider,
    QuotaExceededError,
    RateLimitError,
    ProviderUnavailableError,
    ProviderError
)

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider using langchain-openai."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        priority: int = 1,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
            priority: Provider priority (1=primary)
            temperature: Model temperature
            max_tokens: Maximum tokens in response
        """
        super().__init__(
            api_key=api_key,
            model=model,
            name="openai",
            priority=priority,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Initialize LangChain ChatOpenAI
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            api_key=api_key,
            model="text-embedding-3-small"
        )
        
        logger.info(f"OpenAI provider initialized with model: {model}")
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Invoke the OpenAI LLM.
        
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
            if kwargs.get('temperature') is not None:
                llm = ChatOpenAI(
                    api_key=self.api_key,
                    model=self.model,
                    temperature=kwargs.get('temperature'),
                    max_tokens=kwargs.get('max_tokens', self.max_tokens)
                )
            
            # Convert dict messages to LangChain message objects
            lc_messages = [
                SystemMessage(content=msg["content"]) if msg["role"] == "system"
                else AIMessage(content=msg["content"]) if msg["role"] in ("assistant", "ai")
                else HumanMessage(content=msg["content"]) if msg["role"] == "user"
                else HumanMessage(content=msg["content"])
                for msg in messages
            ]
            
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
            lc_messages = [
                SystemMessage(content=msg["content"]) if msg["role"] == "system"
                else AIMessage(content=msg["content"]) if msg["role"] in ("assistant", "ai")
                else HumanMessage(content=msg["content"]) if msg["role"] == "user"
                else HumanMessage(content=msg["content"])
                for msg in messages
            ]
            
            # Invoke with tools
            response = llm_with_tools.invoke(lc_messages)
            
            self.record_success()
            return response
            
        except Exception as e:
            self.record_error(e)
            self.handle_error(e)
    
    def get_structured_output(self, messages: List[Dict[str, str]], response_format, **kwargs):
        """
        Get structured output using OpenAI function calling.
        
        Args:
            messages: List of message dicts
            response_format: Pydantic model class
            **kwargs: Additional parameters
            
        Returns:
            Instance of response_format
        """
        try:
            self.record_request()
            
            # Use configured LLM with structured output
            llm = self.llm
            structured_llm = llm.with_structured_output(response_format, method="function_calling")
            
            # Convert messages
            lc_messages = [
                SystemMessage(content=msg["content"]) if msg["role"] == "system"
                else HumanMessage(content=msg["content"]) if msg["role"] == "user"
                else AIMessage(content=msg["content"])
                for msg in messages
            ]
            
            response = structured_llm.invoke(lc_messages)
            self.record_success()
            return response
            
        except Exception as e:
            self.record_error(e)
            self.handle_error(e)
    
    def get_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            logger.debug(f"OpenAI: Generating embeddings for text ({len(text)} chars)")
            embeddings = self.embeddings.embed_query(text)
            return embeddings
            
        except Exception as e:
            logger.error(f"OpenAI: Embeddings error - {str(e)}")
            raise ProviderError(f"OpenAI embeddings error: {str(e)}")
    
    def handle_error(self, error: Exception):
        """
        Handle and classify errors from OpenAI API.
        
        Args:
            error: The exception that occurred
            
        Raises:
            QuotaExceededError: If quota is exceeded (429)
            RateLimitError: If rate limit is hit
            ProviderUnavailableError: If service is unavailable
            ProviderError: For other errors
        """
        error_str = str(error).lower()
        
        # Check for quota exceeded (429 status)
        if "429" in error_str or "quota" in error_str or "rate_limit_exceeded" in error_str:
            logger.error(f"OpenAI: Quota exceeded - {error}")
            self.open_circuit_breaker(cooldown_seconds=300)  # 5 minutes
            raise QuotaExceededError(f"OpenAI quota exceeded: {error}")
        
        # Check for rate limiting
        if "rate" in error_str and "limit" in error_str:
            logger.error(f"OpenAI: Rate limit - {error}")
            self.open_circuit_breaker(cooldown_seconds=60)  # 1 minute
            raise RateLimitError(f"OpenAI rate limit: {error}")
        
        # Check for service unavailable
        if "503" in error_str or "unavailable" in error_str or "timeout" in error_str:
            logger.error(f"OpenAI: Service unavailable - {error}")
            raise ProviderUnavailableError(f"OpenAI unavailable: {error}")
        
        # Generic error
        logger.error(f"OpenAI: Error - {error}")
        raise ProviderError(f"OpenAI error: {error}")
