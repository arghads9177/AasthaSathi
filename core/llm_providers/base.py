"""
Base provider abstraction for LLM providers.

This module defines the abstract base class that all LLM providers must implement,
ensuring a consistent interface for the fallback system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class QuotaExceededError(ProviderError):
    """Raised when provider quota is exceeded."""
    pass


class RateLimitError(ProviderError):
    """Raised when rate limit is hit."""
    pass


class ProviderUnavailableError(ProviderError):
    """Raised when provider is temporarily unavailable."""
    pass


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers.
    
    All provider implementations must inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str,
        name: str,
        priority: int = 1,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ):
        """
        Initialize base provider.
        
        Args:
            api_key: API key for the provider
            model: Model name to use
            name: Provider name (e.g., "openai", "groq", "gemini")
            priority: Provider priority (1=highest, 2=fallback, 3=last resort)
            temperature: Model temperature setting
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key
        self.model = model
        self.name = name
        self.priority = priority
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Health tracking
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.last_error = None
        self.last_success_time = None
        self.last_error_time = None
        
        # Circuit breaker
        self.is_circuit_open = False
        self.circuit_open_until = None
        
        logger.info(f"Initialized {self.name} provider with model {self.model}")
    
    @abstractmethod
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Invoke the LLM with messages.
        
        Args:
            messages: List of message dicts [{"role": "...", "content": "..."}]
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Response text
        """
        pass
    
    @abstractmethod
    def invoke_with_tools(self, messages: List[Dict[str, str]], tools: List, **kwargs):
        """
        Invoke the LLM with tool calling support.
        
        Args:
            messages: List of message dicts
            tools: List of tools to bind
            **kwargs: Additional parameters
            
        Returns:
            LLM response with potential tool calls
        """
        pass
    
    @abstractmethod
    def get_structured_output(self, messages: List[Dict[str, str]], response_format, **kwargs):
        """
        Get structured output (Pydantic model).
        
        Args:
            messages: List of message dicts
            response_format: Pydantic model class
            **kwargs: Additional parameters
            
        Returns:
            Instance of response_format
        """
        pass
    
    @abstractmethod
    def get_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        pass
    
    def record_success(self):
        """Record a successful request."""
        self.success_count += 1
        self.last_success_time = datetime.now()
        
        # Close circuit breaker on success
        if self.is_circuit_open:
            logger.info(f"{self.name}: Circuit breaker closed - provider recovered")
            self.is_circuit_open = False
            self.circuit_open_until = None
    
    def record_error(self, error: Exception):
        """Record a failed request."""
        self.error_count += 1
        self.last_error = str(error)
        self.last_error_time = datetime.now()
        
        logger.warning(f"{self.name}: Error recorded - {str(error)[:100]}")
    
    def record_request(self):
        """Record that a request was made."""
        self.request_count += 1
    
    def is_healthy(self) -> bool:
        """
        Check if provider is healthy and available.
        
        Returns:
            True if provider is healthy, False otherwise
        """
        # Check circuit breaker
        if self.is_circuit_open:
            if self.circuit_open_until and datetime.now() < self.circuit_open_until:
                logger.debug(f"{self.name}: Circuit breaker still open")
                return False
            else:
                # Try to recover
                logger.info(f"{self.name}: Circuit breaker timeout expired, attempting recovery")
                self.is_circuit_open = False
        
        # No requests yet - assume healthy
        if self.request_count == 0:
            return True
        
        # Calculate error rate
        error_rate = self.error_count / self.request_count
        
        # Consider unhealthy if error rate > 50%
        if error_rate > 0.5:
            logger.warning(f"{self.name}: High error rate ({error_rate:.1%})")
            return False
        
        return True
    
    def open_circuit_breaker(self, cooldown_seconds: int = 60):
        """
        Open circuit breaker to prevent using this provider temporarily.
        
        Args:
            cooldown_seconds: How long to keep circuit open
        """
        from datetime import timedelta
        
        self.is_circuit_open = True
        self.circuit_open_until = datetime.now() + timedelta(seconds=cooldown_seconds)
        logger.warning(f"{self.name}: Circuit breaker opened for {cooldown_seconds}s")
    
    def get_health_stats(self) -> Dict[str, Any]:
        """
        Get provider health statistics.
        
        Returns:
            Dictionary with health metrics
        """
        error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
        success_rate = (self.success_count / self.request_count * 100) if self.request_count > 0 else 0
        
        return {
            "name": self.name,
            "model": self.model,
            "priority": self.priority,
            "healthy": self.is_healthy(),
            "circuit_open": self.is_circuit_open,
            "request_count": self.request_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": round(success_rate, 2),
            "error_rate": round(error_rate, 2),
            "last_success": self.last_success_time.isoformat() if self.last_success_time else None,
            "last_error": self.last_error_time.isoformat() if self.last_error_time else None,
            "last_error_message": self.last_error
        }
    
    def __repr__(self) -> str:
        """String representation of provider."""
        return f"{self.__class__.__name__}(name='{self.name}', model='{self.model}', priority={self.priority})"
