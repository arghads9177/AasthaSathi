"""
Test the full integrated agent workflow with Banglish query.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.integrated_agent import get_integrated_agent

def test_integrated_agent_banglish():
    """Test the full workflow with Banglish query."""
    
    banglish_query = "Amar member number SM-1388. amar ki ki running account ache?"
    
    print("=" * 80)
    print("TEST: Integrated Agent with Banglish Query")
    print("=" * 80)
    print(f"Query: {banglish_query}")
    print()
    
    # Get integrated agent
    agent = get_integrated_agent()
    
    # Process query
    result = agent.query(banglish_query)
    
    print(f"Answer: {result['answer']}")
    print()
    print(f"Datasource: {result.get('datasource')}")
    print(f"Execution Path: {result.get('execution_path')}")
    print()
    
    # Analyze the result
    if "couldn't find any member" in result['answer'] or "not found" in result['answer'].lower():
        print("✗ ISSUE FOUND: Member not found error")
        print("  This means the workflow is passing wrong data to API")
    elif 'SM-1388' in result['answer'] or 'FD-4117' in result['answer']:
        print("✓ SUCCESS: Found member data")
    else:
        print("? UNCLEAR: Response doesn't clearly indicate success or failure")
    
    print()
    print("Full Answer:")
    print("-" * 80)
    print(result['answer'])
    print("-" * 80)
    
    # Check state debugging
    if 'state_debug' in result:
        print("\nState Debug Info:")
        print(f"  Original Query: {result['state_debug'].get('original_query')}")
        print(f"  Detected Language: {result['state_debug'].get('query_language')}")
        print(f"  Translated Query: {result['state_debug'].get('translated_query')}")
        print(f"  User Query (for API): {result['state_debug'].get('user_query')}")

def test_english_for_comparison():
    """Test with proper English for comparison."""
    
    english_query = "My member number is SM-1388. What running accounts do I have?"
    
    print("\n" + "=" * 80)
    print("TEST: Integrated Agent with Proper English")
    print("=" * 80)
    print(f"Query: {english_query}")
    print()
    
    agent = get_integrated_agent()
    result = agent.query(english_query)
    
    print(f"Answer: {result['answer']}")
    print()
    
    if "couldn't find any member" in result['answer']:
        print("✗ Member not found")
    else:
        print("✓ SUCCESS")

if __name__ == "__main__":
    test_integrated_agent_banglish()
    test_english_for_comparison()
