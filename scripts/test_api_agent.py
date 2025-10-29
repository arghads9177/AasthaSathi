"""
Test script for API Agent.

This script tests the API agent with various queries and scenarios,
including error handling and edge cases.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.api_agent import APIAgent


def test_branch_queries():
    """Test branch-related queries."""
    print("=" * 80)
    print("Testing Branch Queries")
    print("=" * 80)
    
    agent = APIAgent()
    
    test_cases = [
        {
            "query": "Find all active branches",
            "api_queries": None
        },
        {
            "query": "Show me branches in Burnpur",
            "api_queries": ["search branches in Burnpur"]
        },
        {
            "query": "List all branches with status Active",
            "api_queries": ["search active branches"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['query']}")
        if test['api_queries']:
            print(f"API Queries: {test['api_queries']}")
        
        result = agent.query(test['query'], test['api_queries'])
        
        print(f"✓ Success: {result['success']}")
        if result['success']:
            print(f"Response Preview: {result['response'][:200]}...")
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
        print("-" * 80)
    
    return True


def test_deposit_scheme_queries():
    """Test deposit scheme queries."""
    print("\n" + "=" * 80)
    print("Testing Deposit Scheme Queries")
    print("=" * 80)
    
    agent = APIAgent()
    
    test_cases = [
        {
            "query": "What are the current FD schemes available?",
            "api_queries": ["search FD deposit schemes"]
        },
        {
            "query": "Show me all running deposit schemes",
            "api_queries": None
        },
        {
            "query": "What are the interest rates for Fixed Deposits?",
            "api_queries": ["search deposit schemes with type FD"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['query']}")
        if test['api_queries']:
            print(f"API Queries: {test['api_queries']}")
        
        result = agent.query(test['query'], test['api_queries'])
        
        print(f"✓ Success: {result['success']}")
        if result['success']:
            print(f"Response Preview: {result['response'][:200]}...")
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
        print("-" * 80)
    
    return True


def test_loan_scheme_queries():
    """Test loan scheme queries."""
    print("\n" + "=" * 80)
    print("Testing Loan Scheme Queries")
    print("=" * 80)
    
    agent = APIAgent()
    
    test_cases = [
        {
            "query": "What loan schemes are available?",
            "api_queries": None
        },
        {
            "query": "Show me all secured loans",
            "api_queries": ["search secured loan schemes"]
        },
        {
            "query": "What are the interest rates for personal loans?",
            "api_queries": ["search unsecured loan schemes"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['query']}")
        if test['api_queries']:
            print(f"API Queries: {test['api_queries']}")
        
        result = agent.query(test['query'], test['api_queries'])
        
        print(f"✓ Success: {result['success']}")
        if result['success']:
            print(f"Response Preview: {result['response'][:200]}...")
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
        print("-" * 80)
    
    return True


def test_hybrid_query_with_context():
    """Test query with additional context."""
    print("\n" + "=" * 80)
    print("Testing Hybrid Query with Context")
    print("=" * 80)
    
    agent = APIAgent()
    
    context = """
    Fixed Deposits (FD) are time deposits where you invest a lump sum amount 
    for a fixed tenure at a predetermined interest rate. The interest rate 
    is generally higher than savings accounts. FDs are considered safe 
    investments and are ideal for risk-averse investors.
    """
    
    query = "Tell me about FD schemes and show me the current rates"
    
    print(f"\nQuery: {query}")
    print(f"Context provided: Yes (FD information from knowledge base)")
    
    result = agent.query_with_context(query, context)
    
    print(f"✓ Success: {result['success']}")
    if result['success']:
        print(f"Response Preview: {result['response'][:300]}...")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")
    print("-" * 80)
    
    return True


def test_error_handling():
    """Test error handling scenarios."""
    print("\n" + "=" * 80)
    print("Testing Error Handling")
    print("=" * 80)
    
    agent = APIAgent()
    
    test_cases = [
        {
            "name": "Empty query",
            "query": "",
            "api_queries": None
        },
        {
            "name": "Very long query",
            "query": "Tell me everything " * 100,
            "api_queries": None
        }
    ]
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Query length: {len(test['query'])} characters")
        
        result = agent.query(test['query'], test['api_queries'])
        
        print(f"Success: {result['success']}")
        if not result['success']:
            print(f"Error handled: {result.get('error', 'Unknown error')[:100]}...")
        print("-" * 80)
    
    return True


def test_multiple_tool_calls():
    """Test queries that require multiple tool calls."""
    print("\n" + "=" * 80)
    print("Testing Multiple Tool Calls")
    print("=" * 80)
    
    agent = APIAgent()
    
    test_cases = [
        {
            "query": "Compare FD and RD deposit schemes",
            "api_queries": ["search FD schemes", "search RD schemes"]
        },
        {
            "query": "Show me branches and loan schemes",
            "api_queries": ["search branches", "search loan schemes"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['query']}")
        print(f"API Queries: {test['api_queries']}")
        
        result = agent.query(test['query'], test['api_queries'])
        
        print(f"✓ Success: {result['success']}")
        if result['success']:
            print(f"Response Preview: {result['response'][:300]}...")
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
        print("-" * 80)
    
    return True


def test_agent_initialization():
    """Test agent initialization with different parameters."""
    print("\n" + "=" * 80)
    print("Testing Agent Initialization")
    print("=" * 80)
    
    try:
        # Test default initialization
        print("\n1. Default initialization")
        agent1 = APIAgent()
        print(f"✓ Model: {agent1.model_name}")
        print(f"✓ Temperature: {agent1.temperature}")
        print(f"✓ Tools: {len(agent1.tools)} tools loaded")
        for tool in agent1.tools:
            print(f"  - {tool.name}")
        
        # Test custom parameters
        print("\n2. Custom parameters")
        agent2 = APIAgent(model_name="gpt-3.5-turbo", temperature=0.5)
        print(f"✓ Model: {agent2.model_name}")
        print(f"✓ Temperature: {agent2.temperature}")
        
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("API AGENT TEST SUITE")
    print("=" * 80 + "\n")
    
    results = {}
    
    # Run tests
    print("Running tests...\n")
    
    results["Agent Initialization"] = test_agent_initialization()
    results["Branch Queries"] = test_branch_queries()
    results["Deposit Scheme Queries"] = test_deposit_scheme_queries()
    results["Loan Scheme Queries"] = test_loan_scheme_queries()
    results["Hybrid Query"] = test_hybrid_query_with_context()
    results["Multiple Tool Calls"] = test_multiple_tool_calls()
    results["Error Handling"] = test_error_handling()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nTotal: {passed_tests}/{total_tests} test suites passed")
    print("=" * 80 + "\n")
    
    if passed_tests == total_tests:
        print("✓ All test suites passed! API Agent is working correctly.")
    else:
        print("✗ Some test suites failed. Please check the errors above.")


if __name__ == "__main__":
    main()
