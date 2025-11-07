"""
Debug the state flow in integrated agent to see what query reaches API node.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
logging.basicConfig(level=logging.INFO)

from agents.integrated_agent import IntegratedAgent
from agents.integration_nodes import language_detection_node, query_translation_node, router_node

def test_state_flow():
    """Debug state at each step of the workflow."""
    
    banglish_query = "Amar member number SM-1388. amar ki ki running account ache?"
    
    print("=" * 80)
    print("STATE FLOW DEBUG")
    print("=" * 80)
    print(f"Input Query: {banglish_query}")
    print()
    
    # Simulate the workflow step by step
    # Step 1: Initial state
    state = {
        "user_query": banglish_query,
        "original_query": None,
        "execution_path": []
    }
    print("STEP 1: Initial State")
    print(f"  user_query: {state['user_query']}")
    print(f"  original_query: {state.get('original_query')}")
    print()
    
    # Step 2: Language detection
    state.update(language_detection_node(state))
    print("STEP 2: After Language Detection")
    print(f"  user_query: {state.get('user_query')}")
    print(f"  original_query: {state.get('original_query')}")
    print(f"  query_language: {state.get('query_language')}")
    print(f"  execution_path: {state.get('execution_path')}")
    print()
    
    # Step 3: Query translation
    state.update(query_translation_node(state))
    print("STEP 3: After Query Translation")
    print(f"  user_query: {state.get('user_query')}")
    print(f"  original_query: {state.get('original_query')}")
    print(f"  translated_query: {state.get('translated_query')}")
    print(f"  execution_path: {state.get('execution_path')}")
    print()
    
    # Step 4: Router
    state.update(router_node(state))
    print("STEP 4: After Router")
    print(f"  user_query: {state.get('user_query')}")
    print(f"  datasource: {state.get('datasource')}")
    print(f"  api_queries: {state.get('api_queries')}")
    print()
    
    print("=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print(f"Query that will be sent to API agent: {state.get('user_query')}")
    print()
    
    if state.get('user_query') == banglish_query:
        print("✓ Query preserved correctly (Banglish intact)")
    else:
        print("✗ Query was modified!")

if __name__ == "__main__":
    test_state_flow()
