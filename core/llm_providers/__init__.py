"""
LLM Provider abstraction layer with automatic fallback.

This package provides a unified interface for multiple LLM providers
(OpenAI, Groq, Gemini) with automatic fallback on errors.
"""

from core.llm_providers.base import (
    BaseLLMProvider,
    ProviderError,
    QuotaExceededError,
    RateLimitError,
    ProviderUnavailableError
)
from core.llm_providers.openai_provider import OpenAIProvider
from core.llm_providers.groq_provider import GroqProvider
from core.llm_providers.gemini_provider import GeminiProvider
from core.llm_providers.provider_manager import ProviderManager

__all__ = [
    "BaseLLMProvider",
    "ProviderError",
    "QuotaExceededError",
    "RateLimitError",
    "ProviderUnavailableError",
    "OpenAIProvider",
    "GroqProvider",
    "GeminiProvider",
    "ProviderManager",
]
