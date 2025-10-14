"""
Banking REST API Integration

Secure wrapper for banking API calls with authentication,
role-based access, and audit logging.
"""

import httpx
import logging
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime, timedelta
import json

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ..core.config import get_settings
from ..core.models import User, UserRole, APIResponse, MemberAccount
from ..core.security import check_permissions, sanitize_member_data
from ..core.logging_config import get_audit_logger


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class BankingAPIClient:
    """Client for banking REST API operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.banking_api_base_url
        self.api_key = self.settings.banking_api_key
        self.timeout = self.settings.banking_api_timeout
        
        # HTTP client with common headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AasthaSathi/1.0"
        }
    
    async def get_member_details(self, member_id: str, user: User) -> Optional[Dict]:
        """Get member account details."""
        
        # Check permissions
        if not check_permissions(user.role, "read_all_accounts") and \
           not check_permissions(user.role, "read_limited_accounts"):
            logger.warning(f"User {user.user_id} lacks permission to access member data")
            return None
        
        endpoint = f"/api/members/{member_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                # Log API call
                audit_logger.log_api_call(
                    user_id=user.user_id,
                    endpoint=endpoint,
                    response_status=str(response.status_code),
                    member_id=member_id
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Sanitize data based on user role
                    sanitized_data = sanitize_member_data(data, user.role)
                    
                    logger.info(f"Retrieved member data for {member_id}")
                    return sanitized_data
                
                elif response.status_code == 404:
                    logger.warning(f"Member {member_id} not found")
                    return None
                
                else:
                    logger.error(f"API error for member {member_id}: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"Error retrieving member {member_id}: {e}")
            return None
    
    async def get_account_balance(self, account_number: str, user: User) -> Optional[Dict]:
        """Get account balance information."""
        
        if not check_permissions(user.role, "read_all_accounts"):
            logger.warning(f"User {user.user_id} lacks permission to access account balances")
            return None
        
        endpoint = f"/api/accounts/{account_number}/balance"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                audit_logger.log_api_call(
                    user_id=user.user_id,
                    endpoint=endpoint,
                    response_status=str(response.status_code)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Retrieved balance for account {account_number}")
                    return data
                
                else:
                    logger.error(f"Failed to get balance for {account_number}: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"Error retrieving balance for {account_number}: {e}")
            return None
    
    async def get_transactions(self, account_number: str, 
                             limit: int = 10, user: User = None) -> Optional[List[Dict]]:
        """Get recent transactions for an account."""
        
        if not check_permissions(user.role, "read_all_accounts"):
            logger.warning(f"User {user.user_id} lacks permission to access transactions")
            return None
        
        endpoint = f"/api/accounts/{account_number}/transactions"
        params = {"limit": limit}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout
                )
                
                audit_logger.log_api_call(
                    user_id=user.user_id,
                    endpoint=f"{endpoint}?limit={limit}",
                    response_status=str(response.status_code)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Retrieved {len(data)} transactions for {account_number}")
                    return data
                
                else:
                    logger.error(f"Failed to get transactions for {account_number}: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"Error retrieving transactions for {account_number}: {e}")
            return None
    
    async def get_loan_details(self, member_id: str, user: User) -> Optional[Dict]:
        """Get loan information for a member."""
        
        if not check_permissions(user.role, "read_all_accounts"):
            logger.warning(f"User {user.user_id} lacks permission to access loan details")
            return None
        
        endpoint = f"/api/members/{member_id}/loans"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                audit_logger.log_api_call(
                    user_id=user.user_id,
                    endpoint=endpoint,
                    response_status=str(response.status_code),
                    member_id=member_id
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Retrieved loan details for member {member_id}")
                    return data
                
                else:
                    logger.error(f"Failed to get loan details for {member_id}: {response.status_code}")
                    return None
        
        except Exception as e:
            logger.error(f"Error retrieving loan details for {member_id}: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if the banking API is accessible."""
        
        endpoint = "/api/health"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    timeout=10
                )
                
                return response.status_code == 200
        
        except Exception as e:
            logger.error(f"Banking API health check failed: {e}")
            return False


# LangChain Tools for Agent Integration

class MemberDetailsTool(BaseTool):
    """LangChain tool for getting member details."""
    
    name = "get_member_details"
    description = "Get member account details by member ID. Use this when asked about a specific member's information."
    
    def __init__(self, api_client: BankingAPIClient, user: User):
        super().__init__()
        self.api_client = api_client
        self.user = user
    
    def _run(self, member_id: str) -> str:
        """Get member details synchronously."""
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.api_client.get_member_details(member_id, self.user)
        )
        
        if result:
            return json.dumps(result, indent=2)
        else:
            return f"Could not retrieve details for member {member_id}"
    
    async def _arun(self, member_id: str) -> str:
        """Get member details asynchronously."""
        result = await self.api_client.get_member_details(member_id, self.user)
        
        if result:
            return json.dumps(result, indent=2)
        else:
            return f"Could not retrieve details for member {member_id}"


class AccountBalanceTool(BaseTool):
    """LangChain tool for getting account balance."""
    
    name = "get_account_balance"
    description = "Get account balance by account number. Use this when asked about account balance or current balance."
    
    def __init__(self, api_client: BankingAPIClient, user: User):
        super().__init__()
        self.api_client = api_client
        self.user = user
    
    def _run(self, account_number: str) -> str:
        """Get account balance synchronously."""
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.api_client.get_account_balance(account_number, self.user)
        )
        
        if result:
            return json.dumps(result, indent=2)
        else:
            return f"Could not retrieve balance for account {account_number}"
    
    async def _arun(self, account_number: str) -> str:
        """Get account balance asynchronously."""
        result = await self.api_client.get_account_balance(account_number, self.user)
        
        if result:
            return json.dumps(result, indent=2)
        else:
            return f"Could not retrieve balance for account {account_number}"


class TransactionsTool(BaseTool):
    """LangChain tool for getting transactions."""
    
    name = "get_transactions"
    description = "Get recent transactions for an account. Use this when asked about transaction history or recent transactions."
    
    def __init__(self, api_client: BankingAPIClient, user: User):
        super().__init__()
        self.api_client = api_client
        self.user = user
    
    def _run(self, account_number: str, limit: int = 10) -> str:
        """Get transactions synchronously."""
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.api_client.get_transactions(account_number, limit, self.user)
        )
        
        if result:
            return json.dumps(result, indent=2)
        else:
            return f"Could not retrieve transactions for account {account_number}"
    
    async def _arun(self, account_number: str, limit: int = 10) -> str:
        """Get transactions asynchronously."""
        result = await self.api_client.get_transactions(account_number, limit, self.user)
        
        if result:
            return json.dumps(result, indent=2)
        else:
            return f"Could not retrieve transactions for account {account_number}"


class LoanDetailsTool(BaseTool):
    """LangChain tool for getting loan details."""
    
    name = "get_loan_details"
    description = "Get loan information for a member by member ID. Use this when asked about loans, loan status, or loan details."
    
    def __init__(self, api_client: BankingAPIClient, user: User):
        super().__init__()
        self.api_client = api_client
        self.user = user
    
    def _run(self, member_id: str) -> str:
        """Get loan details synchronously."""
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            self.api_client.get_loan_details(member_id, self.user)
        )
        
        if result:
            return json.dumps(result, indent=2)
        else:
            return f"Could not retrieve loan details for member {member_id}"
    
    async def _arun(self, member_id: str) -> str:
        """Get loan details asynchronously."""
        result = await self.api_client.get_loan_details(member_id, self.user)
        
        if result:
            return json.dumps(result, indent=2)
        else:
            return f"Could not retrieve loan details for member {member_id}"


def create_banking_tools(user: User) -> List[BaseTool]:
    """Create LangChain tools for banking API access."""
    
    api_client = BankingAPIClient()
    
    tools = [
        MemberDetailsTool(api_client, user),
        AccountBalanceTool(api_client, user),
        TransactionsTool(api_client, user),
        LoanDetailsTool(api_client, user)
    ]
    
    return tools


# Mock API Client for Development/Testing

class MockBankingAPIClient(BankingAPIClient):
    """Mock banking API client for testing without real API."""
    
    def __init__(self):
        self.settings = get_settings()
        # Don't call parent init to avoid API key requirements
        
        # Mock data
        self.mock_members = {
            "12345": {
                "member_id": "12345",
                "name": "Rajesh Kumar",
                "account_number": "ACC001",
                "balance": 50000.00,
                "schemes": [
                    {"name": "Savings Account", "balance": 25000.00},
                    {"name": "Fixed Deposit", "balance": 25000.00, "maturity": "2024-12-31"}
                ],
                "status": "Active",
                "phone": "9876543210",
                "email": "rajesh@example.com"
            },
            "67890": {
                "member_id": "67890", 
                "name": "Priya Sharma",
                "account_number": "ACC002",
                "balance": 75000.00,
                "schemes": [
                    {"name": "Savings Account", "balance": 15000.00},
                    {"name": "Recurring Deposit", "balance": 60000.00}
                ],
                "status": "Active",
                "phone": "9123456789",
                "email": "priya@example.com"
            }
        }
    
    async def get_member_details(self, member_id: str, user: User) -> Optional[Dict]:
        """Mock member details retrieval."""
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        if member_id in self.mock_members:
            data = self.mock_members[member_id].copy()
            
            # Apply role-based data sanitization
            sanitized_data = sanitize_member_data(data, user.role)
            
            # Log the mock API call
            audit_logger.log_api_call(
                user_id=user.user_id,
                endpoint=f"/api/members/{member_id}",
                response_status="200",
                member_id=member_id
            )
            
            return sanitized_data
        
        return None
    
    async def get_account_balance(self, account_number: str, user: User) -> Optional[Dict]:
        """Mock account balance retrieval."""
        
        await asyncio.sleep(0.1)
        
        # Find member by account number
        for member_data in self.mock_members.values():
            if member_data["account_number"] == account_number:
                audit_logger.log_api_call(
                    user_id=user.user_id,
                    endpoint=f"/api/accounts/{account_number}/balance",
                    response_status="200"
                )
                
                return {
                    "account_number": account_number,
                    "balance": member_data["balance"],
                    "currency": "INR",
                    "last_updated": datetime.now().isoformat()
                }
        
        return None
    
    async def health_check(self) -> bool:
        """Mock health check."""
        return True


def create_api_client(use_mock: bool = False) -> BankingAPIClient:
    """Factory function to create API client."""
    
    if use_mock:
        return MockBankingAPIClient()
    else:
        return BankingAPIClient()


if __name__ == "__main__":
    # Test the API client
    async def test_api():
        from ..core.models import User, UserRole
        
        # Create test user
        user = User(
            user_id="test_user",
            username="test",
            role=UserRole.EMPLOYEE
        )
        
        # Test with mock client
        client = create_api_client(use_mock=True)
        
        # Test member details
        member_data = await client.get_member_details("12345", user)
        print(f"Member data: {json.dumps(member_data, indent=2)}")
        
        # Test account balance
        balance_data = await client.get_account_balance("ACC001", user)
        print(f"Balance data: {json.dumps(balance_data, indent=2)}")
        
        # Test health check
        health = await client.health_check()
        print(f"API Health: {health}")
    
    asyncio.run(test_api())