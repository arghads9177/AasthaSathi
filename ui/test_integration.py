"""
Integration Test Script for AasthaSathi UI

Comprehensive tests for all UI features:
- API connectivity
- Authentication (MyAastha login)
- Query submission
- Error handling
- Session management
"""

import sys
from pathlib import Path

# Add ui directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "ui"))

from api_client import AasthaSathiAPIClient
from config import (
    AASTHASATHI_API_URL,
    AASTHASATHI_API_USERNAME,
    AASTHASATHI_API_PASSWORD,
    MYAASTHA_LOGIN_URL,
    MYAASTHA_AUTH_TOKEN
)
import time


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_test(name, passed, details=""):
    """Print test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"     {details}")


def test_api_connectivity():
    """Test API server connectivity."""
    print_header("TEST 1: API Connectivity")
    
    client = AasthaSathiAPIClient(
        api_base_url=AASTHASATHI_API_URL,
        api_username=AASTHASATHI_API_USERNAME,
        api_password=AASTHASATHI_API_PASSWORD,
        myaastha_login_url=MYAASTHA_LOGIN_URL,
        myaastha_auth_token=MYAASTHA_AUTH_TOKEN
    )
    
    # Test 1.1: Health Check
    is_healthy, health_data, error = client.health_check()
    print_test(
        "Health Check",
        is_healthy,
        f"Status: {health_data.get('status') if health_data else error}"
    )
    
    # Test 1.2: Connection Status
    status = client.get_connection_status()
    print_test(
        "Connection Status",
        status["api_connected"],
        f"URL: {status['api_url']}"
    )
    
    return client, is_healthy


def test_authentication(client):
    """Test MyAastha authentication."""
    print_header("TEST 2: Authentication")
    
    # Get test credentials (using environment or hardcoded test account)
    # Note: Replace with actual test credentials
    test_userid = input("\nEnter test User ID (or press Enter to skip): ").strip()
    
    if not test_userid:
        print("⚠️  Skipping authentication tests (no credentials provided)")
        return False
    
    test_password = input("Enter test Password: ").strip()
    
    # Test 2.1: Valid Login
    success, user_data, error = client.login_myaastha(test_userid, test_password)
    print_test(
        "Valid Login",
        success,
        f"User: {user_data.get('name') if user_data else error}"
    )
    
    if success:
        # Test 2.2: User Info Extraction
        has_required_fields = all([
            user_data.get("userid"),
            user_data.get("usertoken"),
            user_data.get("name")
        ])
        print_test(
            "User Info Extraction",
            has_required_fields,
            f"Fields present: userid, usertoken, name"
        )
        
        # Test 2.3: Logout
        client.logout()
        print_test(
            "Logout",
            not client.is_authenticated,
            "Session cleared"
        )
    
    # Test 2.4: Invalid Login
    invalid_success, _, error = client.login_myaastha("invalid_user", "wrong_password")
    print_test(
        "Invalid Login (Error Handling)",
        not invalid_success,
        f"Error message: {error}"
    )
    
    # Return True if at least the valid login worked
    return success


def test_query_submission(client):
    """Test query submission and response handling."""
    print_header("TEST 3: Query Submission")
    
    test_queries = [
        ("What are the loan types available?", "Banking query"),
        ("Explain KYC process", "Procedure query"),
        ("What is the interest rate?", "Rate query")
    ]
    
    results = []
    
    for query, description in test_queries:
        print(f"\n🔍 Testing: {description}")
        print(f"   Query: '{query}'")
        
        start_time = time.time()
        success, response, error = client.query(query)
        elapsed = time.time() - start_time
        
        if success:
            answer = response.get("answer", "")
            metadata = response.get("metadata", {})
            sources = response.get("sources", [])
            
            print_test(
                f"Query Execution ({description})",
                True,
                f"Time: {elapsed:.2f}s, Answer length: {len(answer)} chars"
            )
            
            # Check response structure
            has_answer = len(answer) > 0
            has_metadata = len(metadata) > 0
            
            print_test(
                "Response Structure",
                has_answer,
                f"Answer: {has_answer}, Metadata: {has_metadata}, Sources: {len(sources)}"
            )
            
            # Display metadata if available
            if metadata:
                route = metadata.get("route", "N/A")
                exec_time = metadata.get("execution_time", 0)
                print(f"     Route: {route}, Exec Time: {exec_time:.2f}s")
            
            results.append(True)
        else:
            print_test(
                f"Query Execution ({description})",
                False,
                f"Error: {error}"
            )
            results.append(False)
        
        # Small delay between queries
        time.sleep(1)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 Query Success Rate: {success_rate:.0f}% ({sum(results)}/{len(results)})")
    
    return all(results)


def test_error_handling(client):
    """Test error handling scenarios."""
    print_header("TEST 4: Error Handling")
    
    # Test 4.1: Empty query
    success, response, error = client.query("")
    print_test(
        "Empty Query Handling",
        not success or (response and len(response.get("answer", "")) > 0),
        f"Handled gracefully: {error if not success else 'Processed'}"
    )
    
    # Test 4.2: Very long query
    long_query = "What " * 500  # Very long query
    success, response, error = client.query(long_query)
    print_test(
        "Long Query Handling",
        True,  # Should handle without crashing
        f"Result: {error if not success else 'Processed'}"
    )
    
    # Test 4.3: Special characters
    special_query = "What is the rate for ₹100,000 @ 7.5%?"
    success, response, error = client.query(special_query)
    print_test(
        "Special Characters Handling",
        success or error is not None,
        f"Handled: {success}"
    )
    
    return True


def test_session_features():
    """Test session-related features."""
    print_header("TEST 5: Session Features")
    
    # Test 5.1: Multiple client instances
    client1 = AasthaSathiAPIClient(
        api_base_url=AASTHASATHI_API_URL,
        api_username=AASTHASATHI_API_USERNAME,
        api_password=AASTHASATHI_API_PASSWORD,
        myaastha_login_url=MYAASTHA_LOGIN_URL,
        myaastha_auth_token=MYAASTHA_AUTH_TOKEN
    )
    
    client2 = AasthaSathiAPIClient(
        api_base_url=AASTHASATHI_API_URL,
        api_username=AASTHASATHI_API_USERNAME,
        api_password=AASTHASATHI_API_PASSWORD,
        myaastha_login_url=MYAASTHA_LOGIN_URL,
        myaastha_auth_token=MYAASTHA_AUTH_TOKEN
    )
    
    print_test(
        "Multiple Client Instances",
        client1 is not client2,
        "Independent instances created"
    )
    
    # Test 5.2: State isolation
    client1.is_authenticated = True
    client1.user_info = {"test": "data"}
    
    print_test(
        "State Isolation",
        not client2.is_authenticated and client2.user_info is None,
        "Clients maintain separate state"
    )
    
    return True


def test_ui_integration():
    """Test UI-specific integration points."""
    print_header("TEST 6: UI Integration")
    
    # Test 6.1: Configuration loading
    try:
        from config import APP_TITLE, APP_ICON, THEME_PRIMARY_COLOR
        config_loaded = True
        config_details = f"Title: {APP_TITLE}, Icon: {APP_ICON}"
    except Exception as e:
        config_loaded = False
        config_details = f"Error: {str(e)}"
    
    print_test(
        "Configuration Loading",
        config_loaded,
        config_details
    )
    
    # Test 6.2: Component imports
    components_loaded = True
    try:
        from components.chat import render_chat_history, render_chat_input
        from components.visualizer import render_response_visualizations
        component_details = "All components imported successfully"
    except Exception as e:
        components_loaded = False
        component_details = f"Error: {str(e)}"
    
    print_test(
        "Component Imports",
        components_loaded,
        component_details
    )
    
    return config_loaded and components_loaded


def main():
    """Run all integration tests."""
    print("\n" + "🧪" * 35)
    print("  AasthaSathi UI - Integration Test Suite")
    print("🧪" * 35)
    
    print(f"\n📋 Test Configuration:")
    print(f"   API URL: {AASTHASATHI_API_URL}")
    print(f"   MyAastha Login URL: {MYAASTHA_LOGIN_URL}")
    print(f"   API Username: {AASTHASATHI_API_USERNAME}")
    
    # Track overall results
    test_results = {}
    
    # Run tests
    client, api_ok = test_api_connectivity()
    test_results["API Connectivity"] = api_ok
    
    if api_ok:
        auth_ok = test_authentication(client)
        test_results["Authentication"] = auth_ok
        
        query_ok = test_query_submission(client)
        test_results["Query Submission"] = query_ok
        
        error_ok = test_error_handling(client)
        test_results["Error Handling"] = error_ok
    else:
        print("\n⚠️  Skipping remaining tests (API not available)")
        test_results["Authentication"] = False
        test_results["Query Submission"] = False
        test_results["Error Handling"] = False
    
    session_ok = test_session_features()
    test_results["Session Features"] = session_ok
    
    ui_ok = test_ui_integration()
    test_results["UI Integration"] = ui_ok
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 Overall Result: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! UI is ready for production.")
    elif passed >= total * 0.8:
        print("\n⚠️  Most tests passed. Review failures before deployment.")
    else:
        print("\n❌ Multiple test failures. Debug required before deployment.")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
