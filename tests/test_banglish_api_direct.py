"""
Test if the API agent can understand and process Banglish queries directly.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.api_agent import APIAgent

def test_banglish_api_call():
    """Test if APIAgent can process Banglish query."""
    
    # The problematic query
    banglish_query = "Amar member number SM-1388. amar ki ki running account ache?"
    
    print("=" * 80)
    print("TEST: API Agent Processing Banglish Query")
    print("=" * 80)
    print(f"Query: {banglish_query}")
    print()
    
    # Create API agent
    api_agent = APIAgent()
    
    # Call the API agent
    result = api_agent.query(banglish_query)
    
    print(f"Success: {result['success']}")
    print(f"Response: {result['response']}")
    if 'error' in result:
        print(f"Error: {result['error']}")
    print()
    
    # Check if SM-1388 was used
    if 'SM-1388' in result['response']:
        print("✓ Member ID SM-1388 found in response")
    else:
        print("✗ Member ID SM-1388 NOT found in response")
    
    # Check the response content
    if "couldn't find any member" in result['response'] or "not found" in result['response'].lower():
        print("✗ Member not found error - API likely received wrong parameters")
    else:
        print("✓ Response seems to have found the member")
    
    print()
    print("Full response:")
    print("-" * 80)
    print(result['response'])
    print("-" * 80)

def test_proper_english_api_call():
    """Test with proper English for comparison."""
    
    english_query = "My member number is SM-1388. What running accounts do I have?"
    
    print("\n" + "=" * 80)
    print("TEST: API Agent Processing Proper English Query")
    print("=" * 80)
    print(f"Query: {english_query}")
    print()
    
    api_agent = APIAgent()
    result = api_agent.query(english_query)
    
    print(f"Success: {result['success']}")
    print(f"Response: {result['response']}")
    print()
    
    if "couldn't find any member" in result['response'] or "not found" in result['response'].lower():
        print("✗ Member not found error")
    else:
        print("✓ Response seems to have found the member")
    
    print()
    print("Full response:")
    print("-" * 80)
    print(result['response'])
    print("-" * 80)

if __name__ == "__main__":
    test_banglish_api_call()
    test_proper_english_api_call()
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print("If both queries return 'member not found', the issue is with the API tools.")
    print("If only Banglish fails, the LLM doesn't understand Banglish properly.")
    print("If both succeed, the issue is elsewhere in the workflow.")
