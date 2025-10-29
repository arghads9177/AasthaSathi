"""
Test script for Cobank API client and tools.

This script tests the API client and LangChain tools to ensure they work correctly.
"""

import sys
import os
import json

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.tools.api_client import CobankAPIClient
from agents.tools.api_tools import get_api_tools


def test_api_client():
    """Test the basic API client functionality."""
    print("=" * 80)
    print("Testing Cobank API Client")
    print("=" * 80)
    
    try:
        client = CobankAPIClient()
        print(f"✓ API Client initialized successfully")
        print(f"  Base URL: {client.base_url}")
        print(f"  Timeout: {client.timeout}s")
        print()
        
        # Test branch search
        print("Testing branch search...")
        branches = client.search_branches({"status": "Active"})
        print(f"✓ Branch search successful")
        print(f"  Found {len(branches)} active branches")
        if branches:
            print(f"  Sample branch: {branches[0].get('name', 'N/A')}")
        print()
        
        # Test deposit scheme search
        print("Testing deposit scheme search...")
        schemes = client.search_deposit_schemes({"status": "Running"})
        print(f"✓ Deposit scheme search successful")
        print(f"  Found {len(schemes)} running deposit schemes")
        if schemes:
            print(f"  Sample scheme: {schemes[0].get('name', 'N/A')}")
        print()
        
        # Test loan scheme search
        print("Testing loan scheme search...")
        loans = client.search_loan_schemes({"status": "Running"})
        print(f"✓ Loan scheme search successful")
        print(f"  Found {len(loans)} running loan schemes")
        if loans:
            print(f"  Sample loan: {loans[0].get('name', 'N/A')}")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ API Client test failed: {str(e)}")
        return False


def test_langchain_tools():
    """Test the LangChain tools."""
    print("=" * 80)
    print("Testing LangChain API Tools")
    print("=" * 80)
    
    try:
        tools = get_api_tools()
        print(f"✓ Successfully loaded {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description.strip().split('.')[0]}")
        print()
        
        # Test each tool
        print("Testing BranchSearchTool...")
        branch_tool = tools[0]
        result = branch_tool._run(status="Active")
        data = json.loads(result) if result.startswith("[") or result.startswith("{") else None
        if data:
            print(f"✓ BranchSearchTool working correctly")
            print(f"  Returned {len(data) if isinstance(data, list) else 1} results")
        else:
            print(f"  Result: {result[:100]}")
        print()
        
        print("Testing DepositSchemeSearchTool...")
        deposit_tool = tools[1]
        result = deposit_tool._run(status="Running")
        data = json.loads(result) if result.startswith("[") or result.startswith("{") else None
        if data:
            print(f"✓ DepositSchemeSearchTool working correctly")
            print(f"  Returned {len(data) if isinstance(data, list) else 1} results")
        else:
            print(f"  Result: {result[:100]}")
        print()
        
        print("Testing LoanSchemeSearchTool...")
        loan_tool = tools[2]
        result = loan_tool._run(status="Running")
        data = json.loads(result) if result.startswith("[") or result.startswith("{") else None
        if data:
            print(f"✓ LoanSchemeSearchTool working correctly")
            print(f"  Returned {len(data) if isinstance(data, list) else 1} results")
        else:
            print(f"  Result: {result[:100]}")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ LangChain tools test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("COBANK API AND TOOLS TEST SUITE")
    print("=" * 80 + "\n")
    
    # Test API client
    client_ok = test_api_client()
    
    # Test LangChain tools
    tools_ok = test_langchain_tools()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"API Client: {'✓ PASSED' if client_ok else '✗ FAILED'}")
    print(f"LangChain Tools: {'✓ PASSED' if tools_ok else '✗ FAILED'}")
    print()
    
    if client_ok and tools_ok:
        print("✓ All tests passed! API integration is ready.")
    else:
        print("✗ Some tests failed. Please check the error messages above.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
