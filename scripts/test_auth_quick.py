#!/usr/bin/env python3
"""
Quick authentication test for the API.
"""

import requests
from requests.auth import HTTPBasicAuth

API_URL = "http://localhost:8000/api/v1/query"

print("\n=== Testing API Authentication ===\n")

# Test 1: No authentication
print("Test 1: No authentication")
try:
    response = requests.post(
        API_URL,
        json={"query": "test"},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✓ Correctly rejected (401 Unauthorized)\n")
    else:
        print(f"✗ Expected 401, got {response.status_code}\n")
        print(response.text)
except Exception as e:
    print(f"✗ Error: {e}\n")

# Test 2: Wrong credentials
print("Test 2: Wrong credentials")
try:
    response = requests.post(
        API_URL,
        json={"query": "test"},
        auth=HTTPBasicAuth("wrong_user", "wrong_pass"),
        timeout=5
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✓ Correctly rejected (401 Unauthorized)\n")
    else:
        print(f"✗ Expected 401, got {response.status_code}\n")
        print(response.text)
except Exception as e:
    print(f"✗ Error: {e}\n")

# Test 3: Correct credentials
print("Test 3: Correct credentials")
try:
    response = requests.post(
        API_URL,
        json={"query": "What is 2+2?"},
        auth=HTTPBasicAuth("aastha_admin", "aastha_secure_2025"),
        timeout=30
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Authentication successful!\n")
        result = response.json()
        print(f"Answer preview: {result['answer'][:100]}...\n")
    else:
        print(f"✗ Expected 200, got {response.status_code}\n")
        print(response.text)
except Exception as e:
    print(f"✗ Error: {e}\n")

print("=== Tests Complete ===\n")
