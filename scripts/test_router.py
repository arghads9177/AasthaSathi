"""
Test script for Query Router.

This script tests the router's ability to correctly classify different types of queries.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.router import QueryRouter


# Test cases with expected routing
TEST_CASES = [
    # API queries - need real-time data
    {
        "query": "Where are branches in Kolkata?",
        "expected": "api",
        "description": "Branch location query"
    },
    {
        "query": "What are the current FD interest rates?",
        "expected": "api",
        "description": "Current deposit rates query"
    },
    {
        "query": "Show me all running loan schemes",
        "expected": "api",
        "description": "Available loan schemes query"
    },
    {
        "query": "List all active branches in Delhi",
        "expected": "api",
        "description": "Branch search query"
    },
    {
        "query": "What deposit schemes are available?",
        "expected": "api",
        "description": "Deposit schemes availability"
    },
    {
        "query": "Find branches near pin code 700001",
        "expected": "api",
        "description": "Branch search by location"
    },
    
    # RAG queries - need document knowledge
    {
        "query": "How do I open a savings account?",
        "expected": "rag",
        "description": "Account opening procedure"
    },
    {
        "query": "What documents are needed for a loan application?",
        "expected": "rag",
        "description": "Loan documentation requirements"
    },
    {
        "query": "Explain the difference between FD and RD",
        "expected": "rag",
        "description": "Banking concept explanation"
    },
    {
        "query": "What are the KYC requirements?",
        "expected": "rag",
        "description": "KYC policy information"
    },
    {
        "query": "How does the interest calculation work?",
        "expected": "rag",
        "description": "Interest calculation process"
    },
    {
        "query": "What is the loan application process?",
        "expected": "rag",
        "description": "Loan process information"
    },
    
    # HYBRID queries - need both
    {
        "query": "Tell me about FD schemes and show current rates",
        "expected": "hybrid",
        "description": "Concept + current data"
    },
    {
        "query": "What branches are in Mumbai and how do I open account there?",
        "expected": "hybrid",
        "description": "Branch locations + procedure"
    },
    {
        "query": "Explain loan options and show available schemes",
        "expected": "hybrid",
        "description": "Loan explanation + current schemes"
    },
    {
        "query": "What are RD schemes, their benefits, and current interest rates?",
        "expected": "hybrid",
        "description": "RD concept + current rates"
    },
]


def test_router_classification():
    """Test the router's classification accuracy."""
    print("=" * 80)
    print("TESTING QUERY ROUTER CLASSIFICATION")
    print("=" * 80)
    print()
    
    router = QueryRouter()
    
    results = {
        "correct": 0,
        "incorrect": 0,
        "total": len(TEST_CASES)
    }
    
    incorrect_cases = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        query = test_case["query"]
        expected = test_case["expected"]
        description = test_case["description"]
        
        print(f"Test {i}/{len(TEST_CASES)}: {description}")
        print(f"Query: \"{query}\"")
        
        try:
            result = router.route(query)
            actual = result.datasource
            
            is_correct = actual == expected
            status = "✓ PASS" if is_correct else "✗ FAIL"
            
            print(f"Expected: {expected}")
            print(f"Actual: {actual}")
            print(f"Reasoning: {result.reasoning}")
            if result.api_queries:
                print(f"API Queries: {result.api_queries}")
            print(f"Status: {status}")
            
            if is_correct:
                results["correct"] += 1
            else:
                results["incorrect"] += 1
                incorrect_cases.append({
                    "query": query,
                    "expected": expected,
                    "actual": actual,
                    "reasoning": result.reasoning
                })
            
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            results["incorrect"] += 1
            incorrect_cases.append({
                "query": query,
                "expected": expected,
                "actual": "ERROR",
                "reasoning": str(e)
            })
        
        print("-" * 80)
        print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {results['total']}")
    print(f"Correct: {results['correct']} ({results['correct']/results['total']*100:.1f}%)")
    print(f"Incorrect: {results['incorrect']} ({results['incorrect']/results['total']*100:.1f}%)")
    print()
    
    if incorrect_cases:
        print("INCORRECT CLASSIFICATIONS:")
        print("-" * 80)
        for case in incorrect_cases:
            print(f"Query: {case['query']}")
            print(f"Expected: {case['expected']} | Actual: {case['actual']}")
            print(f"Reasoning: {case['reasoning']}")
            print()
    
    accuracy = results['correct'] / results['total'] * 100
    
    if accuracy >= 90:
        print("✓ EXCELLENT: Router classification accuracy is >= 90%")
    elif accuracy >= 80:
        print("✓ GOOD: Router classification accuracy is >= 80%")
    elif accuracy >= 70:
        print("⚠ ACCEPTABLE: Router classification accuracy is >= 70%")
    else:
        print("✗ NEEDS IMPROVEMENT: Router classification accuracy is < 70%")
    
    print("=" * 80)
    print()
    
    return results


def test_router_edge_cases():
    """Test router with edge cases and ambiguous queries."""
    print("=" * 80)
    print("TESTING EDGE CASES")
    print("=" * 80)
    print()
    
    router = QueryRouter()
    
    edge_cases = [
        "What is Aastha bank?",
        "Tell me everything about savings accounts",
        "I want a loan",
        "Help me with my account",
        "Branch",
        "",
        "What services do you offer?",
    ]
    
    for i, query in enumerate(edge_cases, 1):
        print(f"Edge Case {i}: \"{query}\"")
        try:
            result = router.route(query)
            print(f"Route: {result.datasource}")
            print(f"Reasoning: {result.reasoning}")
            if result.api_queries:
                print(f"API Queries: {result.api_queries}")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 80)
        print()


def main():
    """Run all router tests."""
    print("\n" + "=" * 80)
    print("QUERY ROUTER TEST SUITE")
    print("=" * 80 + "\n")
    
    # Test classification accuracy
    results = test_router_classification()
    
    # Test edge cases
    test_router_edge_cases()
    
    print("=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
