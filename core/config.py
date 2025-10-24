"""
Configuration Management for AasthaSathi

Handles environment variables, API keys, and application settings.
"""

import os
from typing import Optional
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    try:
        from pydantic import BaseSettings, Field
    except ImportError:
        raise ImportError("Please install pydantic-settings: pip install pydantic-settings")


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = "AasthaSathi"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    
    # LLM Configuration
    default_llm_provider: str = Field(default="openai", env="DEFAULT_LLM_PROVIDER")  # "openai" or "gemini"
    default_model: str = Field(default="gpt-4", env="DEFAULT_MODEL")
    temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2000, env="LLM_MAX_TOKENS")
    
    # Embeddings Configuration
    embedding_provider: str = Field(default="openai", env="EMBEDDING_PROVIDER")
    embedding_model: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=1536, env="EMBEDDING_DIMENSION")
    
    # Vector Database
    vector_db_path: str = Field(default="./data/vector_db", env="VECTOR_DB_PATH")
    chroma_collection_name: str = Field(default="aastha_knowledge", env="CHROMA_COLLECTION")
    
    # Chunking Configuration
    chunk_size: int = Field(default=1200, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    # Website Scraping
    website_base_url: str = Field(default="http://myaastha.in", env="WEBSITE_BASE_URL")
    scraping_delay: float = Field(default=1.0, env="SCRAPING_DELAY")  # seconds between requests
    
    # Banking API Configuration
    banking_api_base_url: Optional[str] = Field(default=None, env="BANKING_API_BASE_URL")
    # banking_api_key: Optional[str] = Field(default=None, env="BANKING_API_KEY")
    banking_auth_key: Optional[str] = Field(default=None, env="BANKING_AUTH_KEY")  # Added missing field
    banking_api_timeout: int = Field(default=30, env="BANKING_API_TIMEOUT")
    
    # Security
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # FastAPI Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/aasthasathi.log", env="LOG_FILE")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=3600, env="RATE_LIMIT_PERIOD")  # seconds
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"  # Ignore extra fields from .env file
    }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def validate_api_keys():
    """Validate that required API keys are present."""
    issues = []
    
    if not settings.openai_api_key and not settings.gemini_api_key:
        issues.append("Either OPENAI_API_KEY or GEMINI_API_KEY must be provided")
    
    if settings.default_llm_provider == "openai" and not settings.openai_api_key:
        issues.append("OPENAI_API_KEY is required when using OpenAI as default provider")
    
    if settings.default_llm_provider == "gemini" and not settings.gemini_api_key:
        issues.append("GEMINI_API_KEY is required when using Gemini as default provider")
    
    if issues:
        raise ValueError("Configuration issues:\n" + "\n".join(f"- {issue}" for issue in issues))


def setup_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        settings.vector_db_path,
        "./data/raw"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)