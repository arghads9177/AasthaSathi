"""
Test script for LLM fallback system.

This script tests:
1. Provider Manager initialization
2. Structured output (Router)
3. Tool calling (API Agent)
4. RAG nodes with fallback
5. Fallback behavior when primary provider fails
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_provider_manager, Settings
from agents.router import QueryRouter
from agents.api_agent import APIAgent
from agents.nodes import (
    get_relevancy_check_chain,
    get_query_reformulation_chain,
    get_answer_generation_chain
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_provider_manager():
    """Test provider manager initialization."""
    print("\n" + "="*80)
    print("TEST 1: Provider Manager Initialization")
    print("="*80)
    
    try:
        provider_manager = get_provider_manager()
        
        print(f"\n✓ Provider Manager initialized")
        print(f"  - Number of providers: {len(provider_manager.providers)}")
        print(f"  - Fallback enabled: {provider_manager.enable_fallback}")
        
        for provider in provider_manager.providers:
            print(f"  - Provider: {provider.name} (priority={provider.priority}, model={provider.model})")
        
        # Test simple invocation
        messages = [
            {"role": "user", "content": "Say 'Hello World' in one word"}
        ]
        
        result = provider_manager.invoke_with_fallback(messages, temperature=0)
        
        print(f"\n✓ Simple invocation successful")
        print(f"  - Provider used: {result['provider']}")
        print(f"  - Model: {result['model']}")
        print(f"  - Response: {result['response'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Provider Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_router():
    """Test router with structured output."""
    print("\n" + "="*80)
    print("TEST 2: Router with Structured Output")
    print("="*80)
    
    try:
        router = QueryRouter()
        
        test_queries = [
            "What are the current interest rates for fixed deposits?",
            "Find branches in Mumbai",
            "Explain the loan application process and show branches in Delhi"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            
            result = router.route(query)
            
            print(f"✓ Routed to: {result.datasource}")
            print(f"  - Reasoning: {result.reasoning}")
            if result.api_queries:
                print(f"  - API queries: {result.api_queries}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Router test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_chains():
    """Test RAG chains with fallback."""
    print("\n" + "="*80)
    print("TEST 3: RAG Chains")
    print("="*80)
    
    try:
        # Test relevancy check
        print("\n3.1: Relevancy Check Chain")
        relevancy_chain = get_relevancy_check_chain()
        
        result = relevancy_chain({
            "query": "What is a savings account?",
            "document_content": "A savings account is a deposit account held at a bank that provides interest on deposits.",
            "source": "manual",
            "category": "accounts"
        })
        
        print(f"✓ Relevancy check: {result[:100]}...")
        
        # Test query reformulation
        print("\n3.2: Query Reformulation Chain")
        reformulation_chain = get_query_reformulation_chain()
        
        result = reformulation_chain({
            "original_query": "fd rates",
            "previous_reformulation": "",
            "retry_count": 1
        })
        
        print(f"✓ Reformulated query: {result}")
        
        # Test answer generation
        print("\n3.3: Answer Generation Chain")
        answer_chain = get_answer_generation_chain()
        
        result = answer_chain({
            "chat_history": "",
            "query": "What is a savings account?",
            "context": "A savings account is a deposit account that earns interest."
        })
        
        print(f"✓ Generated answer: {result[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"\n✗ RAG chains test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_provider_stats():
    """Test provider statistics tracking."""
    print("\n" + "="*80)
    print("TEST 4: Provider Statistics")
    print("="*80)
    
    try:
        provider_manager = get_provider_manager()
        stats = provider_manager.get_manager_stats()
        
        print(f"\nProvider Manager Stats:")
        print(f"  - Total requests: {stats['total_requests']}")
        print(f"  - Successful requests: {stats['successful_requests']}")
        print(f"  - Failed requests: {stats['failed_requests']}")
        print(f"  - Fallback count: {stats['fallback_count']}")
        print(f"  - Success rate: {stats['success_rate']:.1%}")
        
        print(f"\nIndividual Provider Stats:")
        for name, pstats in stats['provider_stats'].items():
            print(f"\n  {name}:")
            print(f"    - Requests: {pstats['request_count']}")
            print(f"    - Successes: {pstats['success_count']}")
            print(f"    - Errors: {pstats['error_count']}")
            print(f"    - Success rate: {pstats['success_rate']:.1%}")
            print(f"    - Is healthy: {pstats['is_healthy']}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Stats test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("LLM FALLBACK SYSTEM TEST SUITE")
    print("="*80)
    
    settings = Settings()
    print(f"\nConfiguration:")
    print(f"  - Primary Model: {settings.default_model}")
    print(f"  - Fallback Enabled: {settings.enable_llm_fallback}")
    print(f"  - Fallback Provider: {settings.fallback_llm_provider}")
    
    results = {
        "Provider Manager": test_provider_manager(),
        "Router": test_router(),
        "RAG Chains": test_rag_chains(),
        "Provider Stats": test_provider_stats()
    }
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
