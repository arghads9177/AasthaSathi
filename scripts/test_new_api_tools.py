"""
Test script for new API tools (Members, Accounts, Balance).

This script tests the newly added tools.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.tools.api_tools import (
    MemberSearchTool,
    MemberCountTool,
    AccountSearchTool,
    AccountCountTool,
    AvailableBalanceTool
)


def test_member_search_tool():
    """Test member search tool."""
    print("=" * 80)
    print("Testing Member Search Tool")
    print("=" * 80)
    
    tool = MemberSearchTool()
    
    # Test 1: Search all members with status
    print("\nTest 1: Search members with status 'Member'")
    result = tool._run(status="Member")
    print(f"Result length: {len(result)} characters")
    print(f"Result preview: {result[:200]}...")
    
    # Test 2: Search by name (if any)
    print("\nTest 2: Search without filters")
    result = tool._run()
    print(f"Result length: {len(result)} characters")
    print(f"Result preview: {result[:200]}...")
    
    print("\n" + "=" * 80)


def test_member_count_tool():
    """Test member count tool."""
    print("\nTesting Member Count Tool")
    print("=" * 80)
    
    tool = MemberCountTool()
    
    # Test 1: Count all members
    print("\nTest 1: Count all members")
    result = tool._run()
    print(f"Result: {result}")
    
    # Test 2: Count by status
    print("\nTest 2: Count members with status 'Member'")
    result = tool._run(status="Member")
    print(f"Result: {result}")
    
    print("\n" + "=" * 80)


def test_account_search_tool():
    """Test account search tool."""
    print("\nTesting Account Search Tool")
    print("=" * 80)
    
    tool = AccountSearchTool()
    
    # Test 1: Search running accounts
    print("\nTest 1: Search accounts with status 'Running'")
    result = tool._run(status="Running")
    print(f"Result length: {len(result)} characters")
    print(f"Result preview: {result[:200]}...")
    
    # Test 2: Search by account type
    print("\nTest 2: Search SB accounts")
    result = tool._run(actype="SB")
    print(f"Result length: {len(result)} characters")
    print(f"Result preview: {result[:200]}...")
    
    print("\n" + "=" * 80)


def test_account_count_tool():
    """Test account count tool."""
    print("\nTesting Account Count Tool")
    print("=" * 80)
    
    tool = AccountCountTool()
    
    # Test 1: Count all accounts
    print("\nTest 1: Count all accounts")
    result = tool._run()
    print(f"Result: {result}")
    
    # Test 2: Count by type
    print("\nTest 2: Count SB accounts")
    result = tool._run(actype="SB")
    print(f"Result: {result}")
    
    # Test 3: Count by status
    print("\nTest 3: Count Running accounts")
    result = tool._run(status="Running")
    print(f"Result: {result}")
    
    print("\n" + "=" * 80)


def test_available_balance_tool():
    """Test available balance tool."""
    print("\nTesting Available Balance Tool")
    print("=" * 80)
    
    tool = AvailableBalanceTool()
    
    # Note: This requires a valid account number
    # We'll test with a sample account number from the search results
    print("\nTest: Get balance for a test account")
    print("Note: This test will use a sample account number.")
    print("If no account is available, it will show an error (expected).")
    
    # First, get a sample account number
    from agents.tools.api_tools import AccountSearchTool
    search_tool = AccountSearchTool()
    search_result = search_tool._run(status="Running")
    
    import json
    try:
        accounts = json.loads(search_result)
        if isinstance(accounts, dict) and "results" in accounts:
            accounts = accounts["results"]
        
        if accounts and len(accounts) > 0:
            sample_account = accounts[0].get("accountno")
            if sample_account:
                print(f"Using account number: {sample_account}")
                result = tool._run(accountno=sample_account)
                print(f"Result: {result}")
            else:
                print("No account number found in results")
        else:
            print("No accounts found to test balance")
    except Exception as e:
        print(f"Could not test balance tool: {str(e)}")
    
    print("\n" + "=" * 80)


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("NEW API TOOLS TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        test_member_search_tool()
        test_member_count_tool()
        test_account_search_tool()
        test_account_count_tool()
        test_available_balance_tool()
        
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80 + "\n")
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
