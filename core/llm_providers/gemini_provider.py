"""
Google Gemini LLM provider implementation.

Wraps Google's Gemini models with error handling and health monitoring.
"""

import logging
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage

from core.llm_providers.base import (
    BaseLLMProvider,
    QuotaExceededError,
    RateLimitError,
    ProviderUnavailableError,
    ProviderError
)

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider using langchain-google-genai."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-pro",
        priority: int = 3,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google API key
            model: Model name (e.g., "gemini-pro", "gemini-1.5-pro")
            priority: Provider priority (3=final fallback)
            temperature: Model temperature
            max_tokens: Maximum tokens in response
        """
        super().__init__(
            api_key=api_key,
            model=model,
            name="gemini",
            priority=priority,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Initialize LangChain ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model,
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=api_key,
            model="models/embedding-001"
        )
        
        logger.info(f"Gemini provider initialized with model: {model}")
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Invoke the Gemini LLM.
        
        Note: Gemini doesn't support system messages, so they're converted to human messages.
        
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
            
            # Convert messages
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
        Get structured output using Gemini's structured output.
        
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
        """
        Convert dict messages to LangChain message objects.
        
        Note: Gemini doesn't support system messages, so they're converted to human messages
        with a prefix.
        """
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                # Gemini limitation: convert system to human with prefix
                lc_messages.append(HumanMessage(content=f"System instruction: {content}"))
            elif role in ("user", "human"):
                lc_messages.append(HumanMessage(content=content))
            elif role in ("assistant", "ai"):
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))
        
        return lc_messages
    
    def get_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings using Gemini.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            logger.debug(f"Gemini: Generating embeddings for text ({len(text)} chars)")
            embeddings = self.embeddings.embed_query(text)
            return embeddings
            
        except Exception as e:
            logger.error(f"Gemini: Embeddings error - {str(e)}")
            raise ProviderError(f"Gemini embeddings error: {str(e)}")
    
    def handle_error(self, error: Exception):
        """
        Handle and classify errors from Gemini API.
        
        Args:
            error: The exception that occurred
            
        Raises:
            QuotaExceededError: If quota is exceeded
            RateLimitError: If rate limit is hit
            ProviderUnavailableError: If service is unavailable
            ProviderError: For other errors
        """
        error_str = str(error).lower()
        
        # Check for resource exhausted (Gemini's quota error)
        if "resource" in error_str and "exhausted" in error_str:
            logger.error(f"Gemini: Resource exhausted - {error}")
            self.open_circuit_breaker(cooldown_seconds=300)  # 5 minutes
            raise QuotaExceededError(f"Gemini quota exceeded: {error}")
        
        # Check for rate limiting
        if "rate" in error_str and "limit" in error_str:
            logger.error(f"Gemini: Rate limit - {error}")
            self.open_circuit_breaker(cooldown_seconds=60)  # 1 minute
            raise RateLimitError(f"Gemini rate limit: {error}")
        
        # Check for service unavailable
        if "503" in error_str or "unavailable" in error_str or "timeout" in error_str:
            logger.error(f"Gemini: Service unavailable - {error}")
            raise ProviderUnavailableError(f"Gemini unavailable: {error}")
        
        # Generic error
        logger.error(f"Gemini: Error - {error}")
        raise ProviderError(f"Gemini error: {error}")
