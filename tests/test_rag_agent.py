"""
Test script for RAG Agent.

Run this to test the complete agentic RAG workflow.

The agent uses LangChain Expression Language (LCEL) for:
- Better composability and maintainability
- Built-in streaming support
- Improved error handling and retries
- Enhanced observability and tracing
- Type-safe chain composition
"""

import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents import get_rag_agent
from core.config import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_rag_agent():
    """Test RAG agent with sample queries."""
    
    logger.info("=" * 80)
    logger.info("RAG AGENT TEST")
    logger.info("=" * 80)
    
    # Validate configuration
    settings = get_settings()
    logger.info(f"Configuration:")
    logger.info(f"  - Model: {settings.rag_model}")
    logger.info(f"  - Temperature: {settings.rag_temperature}")
    logger.info(f"  - Retrieval K: {settings.rag_retrieval_k}")
    logger.info(f"  - Max Retries: {settings.rag_max_retries}")
    logger.info("")
    
    # Initialize agent
    agent = get_rag_agent()
    
    # Test queries
    test_queries = [
        "What is the interest rate for fixed deposits?",
        "How do I register in the MyAastha app?",
        "What are the different types of loans available?",
        # "Tell me about recent stock market trends",  # Should trigger fallback
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n{'=' * 80}")
        logger.info(f"TEST QUERY {i}/{len(test_queries)}")
        logger.info(f"{'=' * 80}")
        logger.info(f"Q: {query}")
        logger.info("-" * 80)
        
        try:
            result = agent.query(query)
            
            logger.info(f"\n✓ ANSWER:")
            logger.info(result["answer"])
            
            logger.info(f"\n📚 SOURCES ({len(result['sources'])}):")
            for source in result["sources"][:3]:  # Show max 3 sources
                logger.info(f"  - {source}")
            
            logger.info(f"\n📊 EXECUTION DETAILS:")
            logger.info(f"  - Path: {' → '.join(result['execution_path'])}")
            logger.info(f"  - Retries: {result['retry_count']}")
            logger.info(f"  - Retrieved: {result['num_retrieved']} documents")
            logger.info(f"  - Relevant: {result['num_relevant']} documents")
            logger.info(f"  - Session: {result['session_id']}")
            
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
    
    logger.info(f"\n{'=' * 80}")
    logger.info("TEST COMPLETED")
    logger.info("=" * 80)


def interactive_mode():
    """Interactive chat mode with RAG agent."""
    
    logger.info("=" * 80)
    logger.info("INTERACTIVE RAG AGENT")
    logger.info("=" * 80)
    logger.info("Type 'quit' or 'exit' to stop")
    logger.info("Type 'clear' to start a new session")
    logger.info("")
    
    agent = get_rag_agent()
    session_id = None
    chat_history = []
    
    while True:
        try:
            # Get user input
            query = input("\n💬 You: ").strip()
            
            if not query:
                continue
            
            # Handle commands
            if query.lower() in ["quit", "exit"]:
                logger.info("Goodbye! 👋")
                break
            
            if query.lower() == "clear":
                session_id = None
                chat_history = []
                logger.info("✓ Session cleared")
                continue
            
            # Query agent
            result = agent.query(
                user_query=query,
                session_id=session_id,
                chat_history=chat_history
            )
            
            # Update session
            session_id = result["session_id"]
            chat_history = result.get("chat_history", [])
            
            # Display answer
            print(f"\n🤖 AasthaSathi: {result['answer']}")
            
            # Display sources (compact)
            if result['sources']:
                print(f"\n📚 Sources: {', '.join(result['sources'][:3])}")
            
            # Display execution info (compact)
            print(f"📊 Path: {' → '.join(result['execution_path'])}")
            
        except KeyboardInterrupt:
            logger.info("\nGoodbye! 👋")
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RAG Agent")
    parser.add_argument(
        "--mode",
        choices=["test", "interactive"],
        default="test",
        help="Test mode: run sample queries or interactive chat"
    )
    
    args = parser.parse_args()
    
    if args.mode == "test":
        test_rag_agent()
    else:
        interactive_mode()
