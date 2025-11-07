"""
Comprehensive Workflow Diagnostics Test Suite

Tests the complete multilingual workflow to identify issues with API calls
after multilingual implementation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.models import AgentState
from agents.integration_nodes import (
    language_detection_node,
    query_translation_node,
    router_node,
    api_call_node
)
from agents.nodes import retrieve_node, check_relevancy_node, generate_answer_node
from agents.integrated_agent import get_integrated_agent


def print_separator(title: str):
    """Print a formatted separator."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_state_summary(state: dict, title: str = "State Summary"):
    """Print key state information."""
    print(f"\n--- {title} ---")
    print(f"User Query: {state.get('user_query', 'N/A')}")
    print(f"Query Language: {state.get('query_language', 'N/A')} (confidence: {state.get('query_language_confidence', 'N/A')})")
    print(f"Original Query: {state.get('original_query', 'N/A')}")
    print(f"Translated Query: {state.get('translated_query', 'N/A')}")
    print(f"Datasource: {state.get('datasource', 'N/A')}")
    print(f"Routing Reasoning: {state.get('routing_reasoning', 'N/A')[:100]}...")
    print(f"API Success: {state.get('api_success', 'N/A')}")
    print(f"API Context: {state.get('api_context', 'N/A')[:100] if state.get('api_context') else 'None'}...")
    print(f"Retrieved Docs: {len(state.get('retrieved_documents', []))}")
    print(f"Final Answer: {state.get('final_answer', 'N/A')[:100] if state.get('final_answer') else 'None'}...")
    print(f"Execution Path: {' → '.join(state.get('execution_path', []))}")
    print("-" * 60)


def test_language_detection():
    """Test language detection with various queries."""
    print_separator("TEST 1: Language Detection Node")
    
    test_cases = [
        ("What is the balance?", "en"),
        ("बैलेंस क्या है?", "hi"),
        ("ব্যালেন্স কত?", "bn"),
        ("How do I check my account balance?", "en"),
        ("खाता शेष कैसे जांचें?", "hi")
    ]
    
    for query, expected_lang in test_cases:
        print(f"\nTesting: '{query}'")
        print(f"Expected: {expected_lang}")
        
        state = AgentState(
            user_query=query,
            messages=[],
            sources_used=[],
            execution_path=[],
            retry_count=0,
            current_doc_index=0,
            is_relevant=False,
            retrieved_documents=[],
            relevant_documents=[]
        )
        
        result = language_detection_node(state)
        
        detected = result.get('query_language', 'unknown')
        confidence = result.get('query_language_confidence', 0.0)
        
        status = "✓ PASS" if detected == expected_lang else "✗ FAIL"
        print(f"Detected: {detected} (confidence: {confidence:.2%}) - {status}")
        
        if detected != expected_lang:
            print(f"  ERROR: Expected {expected_lang} but got {detected}")
    
    print("\n" + "=" * 80)


def test_query_translation():
    """Test query translation node."""
    print_separator("TEST 2: Query Translation Node")
    
    test_cases = [
        ("What is the balance?", "en", "What is the balance?"),  # No translation needed
        ("बैलेंस क्या है?", "hi", None),  # Should translate to English
        ("ব্যালেন্স কত?", "bn", None),  # Should translate to English
    ]
    
    for query, lang, expected_translation in test_cases:
        print(f"\nTesting: '{query}' (lang: {lang})")
        
        state = AgentState(
            user_query=query,
            query_language=lang,
            query_language_confidence=0.95,
            messages=[],
            sources_used=[],
            execution_path=["language_detection"],
            retry_count=0,
            current_doc_index=0,
            is_relevant=False,
            retrieved_documents=[],
            relevant_documents=[]
        )
        
        result = query_translation_node(state)
        
        translated = result.get('translated_query')
        original = result.get('original_query')
        
        print(f"Original Query: {original}")
        print(f"Translated Query: {translated}")
        
        if lang == "en":
            status = "✓ PASS" if translated == query else "✗ FAIL"
            print(f"Status: {status} (English query should not be translated)")
        else:
            status = "✓ PASS" if translated and translated != query else "✗ FAIL"
            print(f"Status: {status} (Non-English query should be translated)")
            if not translated or translated == query:
                print(f"  ERROR: Translation failed or not performed")
    
    print("\n" + "=" * 80)


def test_router_with_api_queries():
    """Test router node with API-type queries."""
    print_separator("TEST 3: Router Node with API Queries")
    
    api_queries = [
        "What is my account balance?",
        "Show me recent transactions",
        "Check my loan status",
        "What is my savings account number?",
        "Get member details for MEM001",
    ]
    
    for query in api_queries:
        print(f"\nTesting: '{query}'")
        
        state = AgentState(
            user_query=query,
            query_language="en",
            query_language_confidence=0.95,
            translated_query=query,
            messages=[],
            sources_used=[],
            execution_path=["language_detection", "query_translation"],
            retry_count=0,
            current_doc_index=0,
            is_relevant=False,
            retrieved_documents=[],
            relevant_documents=[]
        )
        
        result = router_node(state)
        
        datasource = result.get('datasource', 'unknown')
        reasoning = result.get('routing_reasoning', 'N/A')
        api_queries_list = result.get('api_queries', [])
        
        print(f"Datasource: {datasource}")
        print(f"Reasoning: {reasoning[:150]}...")
        print(f"API Queries: {api_queries_list}")
        
        status = "✓ PASS" if datasource in ['api', 'hybrid'] else "✗ FAIL"
        print(f"Status: {status} (Expected 'api' or 'hybrid', got '{datasource}')")
        
        if datasource not in ['api', 'hybrid']:
            print(f"  ERROR: API query routed to '{datasource}' instead of 'api' or 'hybrid'")
    
    print("\n" + "=" * 80)


def test_router_with_rag_queries():
    """Test router node with RAG-type queries."""
    print_separator("TEST 4: Router Node with RAG Queries")
    
    rag_queries = [
        "What documents are required for opening an account?",
        "What are the loan types available?",
        "What is the KYC process?",
        "What are the interest rates for fixed deposits?",
    ]
    
    for query in rag_queries:
        print(f"\nTesting: '{query}'")
        
        state = AgentState(
            user_query=query,
            query_language="en",
            query_language_confidence=0.95,
            translated_query=query,
            messages=[],
            sources_used=[],
            execution_path=["language_detection", "query_translation"],
            retry_count=0,
            current_doc_index=0,
            is_relevant=False,
            retrieved_documents=[],
            relevant_documents=[]
        )
        
        result = router_node(state)
        
        datasource = result.get('datasource', 'unknown')
        reasoning = result.get('routing_reasoning', 'N/A')
        
        print(f"Datasource: {datasource}")
        print(f"Reasoning: {reasoning[:150]}...")
        
        status = "✓ PASS" if datasource in ['rag', 'hybrid'] else "✗ FAIL"
        print(f"Status: {status} (Expected 'rag' or 'hybrid', got '{datasource}')")
        
        if datasource not in ['rag', 'hybrid']:
            print(f"  ERROR: RAG query routed to '{datasource}' instead of 'rag' or 'hybrid'")
    
    print("\n" + "=" * 80)


def test_api_call_node():
    """Test API call node with sample queries."""
    print_separator("TEST 5: API Call Node")
    
    test_cases = [
        ("What is my account balance?", ["get_member_balance", "get_account_balance"]),
        ("Show me recent transactions", ["get_member_transactions"]),
        ("Get member details", ["get_member_details"]),
    ]
    
    for query, api_queries in test_cases:
        print(f"\nTesting: '{query}'")
        print(f"API Queries: {api_queries}")
        
        state = AgentState(
            user_query=query,
            query_language="en",
            translated_query=query,
            datasource="api",
            api_queries=api_queries,
            messages=[],
            sources_used=[],
            execution_path=["language_detection", "query_translation", "router"],
            retry_count=0,
            current_doc_index=0,
            is_relevant=False,
            retrieved_documents=[],
            relevant_documents=[]
        )
        
        result = api_call_node(state)
        
        api_success = result.get('api_success', False)
        api_context = result.get('api_context', '')
        sources = result.get('sources_used', [])
        
        print(f"API Success: {api_success}")
        print(f"API Context Length: {len(api_context) if api_context else 0} chars")
        print(f"Sources: {sources}")
        
        status = "✓ PASS" if api_success and api_context else "⚠ WARNING" if not api_success else "✗ FAIL"
        print(f"Status: {status}")
        
        if not api_context:
            print(f"  WARNING: No API context returned (this may be expected if API is unavailable)")
    
    print("\n" + "=" * 80)


def test_full_workflow_api():
    """Test complete workflow with API queries."""
    print_separator("TEST 6: Full Workflow - API Queries")
    
    agent = get_integrated_agent()
    
    test_cases = [
        ("What is my account balance?", "en"),
        ("Show member details", "en"),
        ("बैलेंस क्या है?", "hi"),  # Hindi: What is the balance?
    ]
    
    for query, language in test_cases:
        print(f"\nTesting: '{query}' (language: {language})")
        print("-" * 60)
        
        try:
            result = agent.query(query, language=language)
            
            print(f"Answer: {result.get('answer', 'N/A')[:200]}...")
            print(f"Datasource: {result.get('datasource', 'N/A')}")
            print(f"Routing: {result.get('routing_reasoning', 'N/A')[:100]}...")
            print(f"API Used: {result.get('api_used', False)}")
            print(f"Query Language: {result.get('query_language', 'N/A')}")
            print(f"Response Language: {result.get('response_language', 'N/A')}")
            print(f"Sources: {len(result.get('sources', []))}")
            print(f"Execution Path: {' → '.join(result.get('execution_path', [])[:8])}...")
            
            # Validate API queries
            datasource = result.get('datasource', '')
            api_used = result.get('api_used', False)
            
            if datasource in ['api', 'hybrid']:
                status = "✓ PASS" if api_used or 'API' in result.get('answer', '') else "⚠ WARNING"
                print(f"Status: {status}")
                if not api_used:
                    print(f"  WARNING: Routed to API but api_used=False")
            else:
                print(f"Status: ✗ FAIL - API query routed to '{datasource}' instead of 'api'")
                
        except Exception as e:
            print(f"Status: ✗ ERROR")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)


def test_full_workflow_rag():
    """Test complete workflow with RAG queries."""
    print_separator("TEST 7: Full Workflow - RAG Queries")
    
    agent = get_integrated_agent()
    
    test_cases = [
        ("What documents are required for opening an account?", "en"),
        ("What are the loan types available?", "en"),
        ("खाता खोलने के लिए क्या आवश्यक है?", "hi"),  # Hindi: What is required to open an account?
    ]
    
    for query, language in test_cases:
        print(f"\nTesting: '{query}' (language: {language})")
        print("-" * 60)
        
        try:
            result = agent.query(query, language=language)
            
            print(f"Answer: {result.get('answer', 'N/A')[:200]}...")
            print(f"Datasource: {result.get('datasource', 'N/A')}")
            print(f"Routing: {result.get('routing_reasoning', 'N/A')[:100]}...")
            print(f"Docs Retrieved: {result.get('num_retrieved', 0)}")
            print(f"Docs Relevant: {result.get('num_relevant', 0)}")
            print(f"Query Language: {result.get('query_language', 'N/A')}")
            print(f"Response Language: {result.get('response_language', 'N/A')}")
            print(f"Sources: {len(result.get('sources', []))}")
            print(f"Execution Path: {' → '.join(result.get('execution_path', [])[:8])}...")
            
            # Validate RAG queries
            datasource = result.get('datasource', '')
            num_relevant = result.get('num_relevant', 0)
            
            if datasource in ['rag', 'hybrid']:
                status = "✓ PASS" if num_relevant > 0 else "⚠ WARNING"
                print(f"Status: {status}")
                if num_relevant == 0:
                    print(f"  WARNING: RAG query but no relevant documents found")
            else:
                print(f"Status: ⚠ INFO - RAG query routed to '{datasource}'")
                
        except Exception as e:
            print(f"Status: ✗ ERROR")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)


def test_translated_query_routing():
    """Test if translated queries are being used for routing."""
    print_separator("TEST 8: Translated Query Routing")
    
    print("Testing if Hindi/Bengali queries are translated before routing...")
    
    # Test with Hindi query about balance (should be API)
    state = AgentState(
        user_query="बैलेंस क्या है?",  # What is the balance?
        query_language="hi",
        query_language_confidence=0.95,
        messages=[],
        sources_used=[],
        execution_path=[],
        retry_count=0,
        current_doc_index=0,
        is_relevant=False,
        retrieved_documents=[],
        relevant_documents=[]
    )
    
    # Step 1: Translate
    print("\nStep 1: Translation")
    state = query_translation_node(state)
    print(f"Original: {state.get('original_query')}")
    print(f"Translated: {state.get('translated_query')}")
    
    # Step 2: Route
    print("\nStep 2: Routing")
    state = router_node(state)
    print(f"Datasource: {state.get('datasource')}")
    print(f"Routing Reasoning: {state.get('routing_reasoning', '')[:150]}...")
    print(f"API Queries: {state.get('api_queries', [])}")
    
    # Validate
    datasource = state.get('datasource', '')
    translated = state.get('translated_query', '')
    
    if translated and translated != state.get('original_query'):
        print("\n✓ Translation successful")
    else:
        print("\n✗ Translation failed or not performed")
    
    if datasource in ['api', 'hybrid']:
        print("✓ Correctly routed to API (balance query)")
    else:
        print(f"✗ FAIL: Balance query routed to '{datasource}' instead of 'api'")
        print("  This suggests translated query may not be used for routing")
    
    print("\n" + "=" * 80)


def main():
    """Run all diagnostic tests."""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "  MULTILINGUAL WORKFLOW DIAGNOSTIC TEST SUITE".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    try:
        # Test individual nodes
        test_language_detection()
        test_query_translation()
        test_router_with_api_queries()
        test_router_with_rag_queries()
        test_api_call_node()
        
        # Test translated query routing (critical test)
        test_translated_query_routing()
        
        # Test full workflows
        test_full_workflow_api()
        test_full_workflow_rag()
        
        print_separator("DIAGNOSTIC TESTS COMPLETED")
        print("\nReview the test results above to identify issues.")
        print("Look for:")
        print("  - ✗ FAIL markers indicating test failures")
        print("  - ⚠ WARNING markers indicating potential issues")
        print("  - API queries being routed to 'rag' instead of 'api'")
        print("  - Translated queries not being used for routing")
        print("  - API call failures or empty responses")
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR during testing:")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
