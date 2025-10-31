"""
LLM Provider Manager with automatic fallback.

Manages multiple LLM providers and automatically falls back to alternative
providers when errors occur (quota exceeded, rate limits, etc.).
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from core.llm_providers.base import (
    BaseLLMProvider,
    QuotaExceededError,
    RateLimitError,
    ProviderUnavailableError,
    ProviderError
)

logger = logging.getLogger(__name__)


class ProviderManager:
    """
    Manages multiple LLM providers with automatic fallback.
    
    Tries providers in priority order until one succeeds. Includes:
    - Automatic error detection and fallback
    - Health monitoring and circuit breaking
    - Usage tracking and statistics
    """
    
    def __init__(self, providers: List[BaseLLMProvider], enable_fallback: bool = True):
        """
        Initialize provider manager.
        
        Args:
            providers: List of provider instances
            enable_fallback: Whether to enable automatic fallback
        """
        # Sort by priority (1=highest priority)
        self.providers = sorted(providers, key=lambda p: p.priority)
        self.enable_fallback = enable_fallback
        
        # Stats
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.fallback_count = 0
        
        logger.info(f"ProviderManager initialized with {len(self.providers)} providers:")
        for p in self.providers:
            logger.info(f"  - {p.name} (priority={p.priority}, model={p.model})")
        logger.info(f"  Fallback enabled: {enable_fallback}")
    
    def invoke_with_fallback(
        self,
        messages: List[Dict[str, str]],
        response_format=None,
        tools=None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Invoke LLM with automatic fallback on errors.
        
        Tries providers in priority order until one succeeds:
        1. Primary provider (e.g., OpenAI)
        2. Fallback 1 (e.g., Groq)
        3. Fallback 2 (e.g., Gemini)
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            response_format: Optional Pydantic model for structured output
            tools: Optional list of tools for tool calling
            **kwargs: Additional parameters
            
        Returns:
            Dict with 'response', 'provider', 'model'
            
        Raises:
            ProviderError: When all providers fail
        """
        self.total_requests += 1
        
        errors = []
        providers_tried = []
        
        for provider in self.providers:
            # Skip unhealthy providers
            if not provider.is_healthy():
                logger.warning(
                    f"Skipping unhealthy provider: {provider.name} "
                    f"(error_rate={provider.error_count}/{provider.request_count})"
                )
                errors.append(f"{provider.name}: Unhealthy (circuit breaker open)")
                continue
            
            try:
                logger.info(f"Trying provider: {provider.name} (model={provider.model})")
                providers_tried.append(provider.name)
                
                # Choose invoke method based on parameters
                if response_format:
                    # Structured output
                    response = provider.get_structured_output(messages, response_format, **kwargs)
                elif tools:
                    # Tool calling
                    response = provider.invoke_with_tools(messages, tools, **kwargs)
                else:
                    # Regular invoke
                    response = provider.invoke(messages, **kwargs)
                
                # Success!
                self.successful_requests += 1
                
                # Log fallback if not primary provider
                if provider.priority > 1:
                    self.fallback_count += 1
                    logger.warning(
                        f"✓ Fallback successful! Used {provider.name} instead of primary provider. "
                        f"(Total fallbacks: {self.fallback_count})"
                    )
                else:
                    logger.info(f"✓ Primary provider {provider.name} succeeded")
                
                return {
                    "response": response,
                    "provider": provider.name,
                    "model": provider.model
                }
                
            except (QuotaExceededError, RateLimitError, ProviderUnavailableError) as e:
                # Expected errors that trigger fallback
                error_msg = f"{provider.name}: {e.__class__.__name__} - {str(e)[:100]}"
                errors.append(error_msg)
                logger.warning(f"Provider {provider.name} failed: {e.__class__.__name__}")
                
                # If fallback disabled, raise immediately
                if not self.enable_fallback:
                    logger.error("Fallback disabled, raising error")
                    self.failed_requests += 1
                    raise
                
                # Try next provider
                logger.info(f"→ Attempting fallback to next provider...")
                continue
                
            except ProviderError as e:
                # Unexpected provider error
                error_msg = f"{provider.name}: {str(e)[:100]}"
                errors.append(error_msg)
                logger.error(f"Provider {provider.name} error: {str(e)[:200]}")
                
                # Try next provider
                if self.enable_fallback:
                    logger.info(f"→ Attempting fallback to next provider...")
                    continue
                else:
                    self.failed_requests += 1
                    raise
            
            except Exception as e:
                # Unexpected error
                error_msg = f"{provider.name}: Unexpected error - {str(e)[:100]}"
                errors.append(error_msg)
                logger.error(f"Unexpected error from {provider.name}: {str(e)[:200]}", exc_info=True)
                
                # Try next provider
                if self.enable_fallback:
                    continue
                else:
                    self.failed_requests += 1
                    raise
        
        # All providers failed
        self.failed_requests += 1
        
        error_summary = "\n".join([f"  - {e}" for e in errors])
        logger.error(
            f"✗ All {len(self.providers)} providers failed!\n"
            f"Providers tried: {', '.join(providers_tried)}\n"
            f"Errors:\n{error_summary}"
        )
        
        raise ProviderError(
            f"All LLM providers failed. Tried {len(providers_tried)} providers: {', '.join(providers_tried)}. "
            f"Last error: {errors[-1] if errors else 'Unknown'}"
        )
    
    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """
        Get provider by name.
        
        Args:
            name: Provider name (e.g., "openai", "groq", "gemini")
            
        Returns:
            Provider instance or None if not found
        """
        for provider in self.providers:
            if provider.name == name:
                return provider
        return None
    
    def get_primary_provider(self) -> BaseLLMProvider:
        """
        Get primary provider (highest priority).
        
        Returns:
            Primary provider instance
        """
        return self.providers[0]
    
    def get_all_health_stats(self) -> List[Dict[str, Any]]:
        """
        Get health stats for all providers.
        
        Returns:
            List of health stat dictionaries
        """
        return [provider.get_health_stats() for provider in self.providers]
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """
        Get provider manager statistics.
        
        Returns:
            Dictionary with manager stats and individual provider stats
        """
        success_rate = (self.successful_requests / self.total_requests) if self.total_requests > 0 else 0
        fallback_rate = (self.fallback_count / self.successful_requests) if self.successful_requests > 0 else 0
        
        provider_stats = {}
        for p in self.providers:
            prov_success_rate = (p.success_count / p.request_count) if p.request_count > 0 else 0
            provider_stats[p.name] = {
                "model": p.model,
                "priority": p.priority,
                "request_count": p.request_count,
                "success_count": p.success_count,
                "error_count": p.error_count,
                "success_rate": prov_success_rate,
                "is_healthy": p.is_healthy()
            }
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate,
            "fallback_count": self.fallback_count,
            "fallback_rate": fallback_rate,
            "provider_stats": provider_stats
        }
    
    def __repr__(self) -> str:
        """String representation."""
        provider_names = ", ".join([p.name for p in self.providers])
        return f"ProviderManager(providers=[{provider_names}], fallback={self.enable_fallback})"
