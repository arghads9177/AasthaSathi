#!/usr/bin/env python3
"""
AasthaSathi - Main Application Entry Point

This is the main entry point for the AasthaSathi AI Assistant.
Run this file to start the application.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from aasthasathi.core.config import get_settings, validate_api_keys, setup_directories
from aasthasathi.core.logging_config import setup_logging


async def main():
    """Main application entry point."""
    
    print("🚀 Starting AasthaSathi - AI Assistant for Aastha Co-operative Credit Society")
    print("=" * 80)
    
    try:
        # Setup logging
        logger = setup_logging()
        logger.info("Starting AasthaSathi application")
        
        # Setup directories
        setup_directories()
        logger.info("Created necessary directories")
        
        # Load and validate configuration
        settings = get_settings()
        logger.info(f"Loaded configuration - Debug mode: {settings.debug}")
        
        # Validate API keys
        validate_api_keys()
        logger.info("API keys validated successfully")
        
        print(f"✅ Configuration loaded successfully")
        print(f"🔑 LLM Provider: {settings.default_llm_provider}")
        print(f"🧠 Model: {settings.default_model}")
        print(f"📊 Embeddings: {settings.embedding_provider}")
        print(f"🌐 Website: {settings.website_base_url}")
        print(f"💾 Vector DB: {settings.vector_db_path}")
        
        # TODO: Initialize components
        print("\n🔧 Components to initialize:")
        print("   📥 Ingestion Layer (Website scraper, PDF processor)")
        print("   🤖 Agent Layer (LangChain/LangGraph orchestration)")
        print("   🧠 LLM Layer (OpenAI/Gemini integration)")
        print("   🔌 API Layer (Banking REST API wrapper)")
        print("   🖥️  Frontend Layer (Gradio interface)")
        
        print(f"\n🎯 Next steps:")
        print("   1. Create .env file from .env.template with your API keys")
        print("   2. Run individual components for testing")
        print("   3. Start full application with FastAPI server")
        
        logger.info("AasthaSathi initialization completed successfully")
        
    except Exception as e:
        print(f"❌ Error during startup: {e}")
        if "API_KEY" in str(e):
            print("\n💡 Please ensure you have:")
            print("   1. Created .env file from .env.template")
            print("   2. Added your OpenAI or Gemini API keys")
            print("   3. Configured other required settings")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
