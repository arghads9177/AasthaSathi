"""
Quick API Query Test - Tests API routing without translation dependency

This test focuses on English queries to isolate the API routing issue
from translation problems.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.models import AgentState
from agents.integration_nodes import router_node, language_detection_node, query_translation_node
from agents.integrated_agent import get_integrated_agent


def print_separator(title: str):
    """Print a formatted separator."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_english_api_queries():
    """Test English API queries through the complete flow."""
    print_separator("ENGLISH API QUERY TEST")
    
    api_test_queries = [
        "What is my account balance?",
        "Show me recent transactions",
        "Get member details for MEM001",
        "Check my loan status",
        "What is my savings account number?"
    ]
    
    print("Testing English API queries (no translation needed)...\n")
    
    for query in api_test_queries:
        print(f"\n{'─' * 80}")
        print(f"Query: '{query}'")
        print('─' * 80)
        
        # Test through nodes
        print("\n1. Language Detection:")
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
        
        state_dict = language_detection_node(state)
        lang = state_dict.get('query_language', 'unknown')
        conf = state_dict.get('query_language_confidence', 0.0)
        print(f"   Language: {lang} (confidence: {conf:.2%})")
        
        # Update state
        for key, value in state_dict.items():
            if key in state:
                state[key] = value
        
        print("\n2. Translation:")
        state_dict = query_translation_node(state)
        translated = state_dict.get('translated_query')
        original = state_dict.get('original_query')
        print(f"   Original: {original}")
        print(f"   Translated: {translated}")
        print(f"   Status: {'✓ Skipped (English)' if lang == 'en' else '✓ Translated'}")
        
        # Update state
        for key, value in state_dict.items():
            if key in state or hasattr(state, key):
                state[key] = value
        
        print("\n3. Routing:")
        state_dict = router_node(state)
        datasource = state_dict.get('datasource', 'unknown')
        reasoning = state_dict.get('routing_reasoning', 'N/A')
        api_queries = state_dict.get('api_queries', [])
        
        print(f"   Datasource: {datasource}")
        print(f"   API Queries: {api_queries}")
        print(f"   Reasoning: {reasoning[:150]}...")
        
        # Check result
        if datasource in ['api', 'hybrid']:
            print(f"\n   ✓ PASS - Correctly routed to {datasource}")
        else:
            print(f"\n   ✗ FAIL - API query routed to '{datasource}' instead of 'api' or 'hybrid'")
            print(f"   This is the problem! API queries are not being recognized.")


def test_full_workflow_english_api():
    """Test complete workflow with English API queries."""
    print_separator("FULL WORKFLOW TEST - ENGLISH API QUERIES")
    
    agent = get_integrated_agent()
    
    test_cases = [
        "What is my account balance?",
        "Show me recent transactions",
        "Get member details",
    ]
    
    for query in test_cases:
        print(f"\nQuery: '{query}'")
        print("-" * 60)
        
        try:
            result = agent.query(query, language="en")
            
            print(f"Datasource: {result.get('datasource', 'N/A')}")
            print(f"API Used: {result.get('api_used', False)}")
            print(f"Routing: {result.get('routing_reasoning', 'N/A')[:100]}...")
            print(f"Answer: {result.get('answer', 'N/A')[:150]}...")
            print(f"Path: {' → '.join(result.get('execution_path', [])[:10])}")
            
            # Validate
            datasource = result.get('datasource', '')
            api_used = result.get('api_used', False)
            
            if datasource in ['api', 'hybrid']:
                if api_used:
                    print(f"\n✓ PASS - API query handled correctly")
                else:
                    print(f"\n⚠ WARNING - Routed to '{datasource}' but api_used={api_used}")
            else:
                print(f"\n✗ FAIL - API query routed to '{datasource}'")
                print("ROOT CAUSE: Router is not identifying API queries correctly")
                
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """Run API query tests."""
    print("\n" + "#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + "  API QUERY DIAGNOSTIC TEST (English Only)".center(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)
    
    try:
        # Test node-by-node first
        test_english_api_queries()
        
        # Then test full workflow
        test_full_workflow_english_api()
        
        print_separator("TEST COMPLETED")
        print("\nSummary:")
        print("  - If routing shows 'rag' instead of 'api' for API queries,")
        print("    the router prompt or classification logic needs adjustment")
        print("  - If routing is correct but api_used=False, check api_call_node")
        print("  - Translation issues are bypassed by using English queries only")
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
