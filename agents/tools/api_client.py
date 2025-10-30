"""
Cobank API Client for AasthaSathi.

This module provides a client for interacting with the Cobank API.
"""

import os
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CobankAPIClient:
    """Client for interacting with the Cobank API."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_token: Optional[str] = None,
        timeout: Optional[int] = None,
        ocode: Optional[str] = None
    ):
        """
        Initialize the Cobank API client.
        
        Args:
            base_url: Base URL for the API. Defaults to env var BANKING_API_BASE_URL.
            api_token: Authentication token. Defaults to env var BANKING_AUTH_KEY.
            timeout: Request timeout in seconds. Defaults to env var BANKING_API_TIMEOUT.
            ocode: Organization code. Defaults to env var BANKING_OCODE.
        """
        self.base_url = base_url or os.getenv("BANKING_API_BASE_URL", "")
        self.api_token = api_token or os.getenv("BANKING_AUTH_KEY", "")
        self.timeout = timeout or int(os.getenv("BANKING_API_TIMEOUT", "30"))
        self.ocode = ocode or os.getenv("BANKING_OCODE", "aastha")
        
        if not self.base_url:
            raise ValueError("BANKING_API_BASE_URL not configured in environment")
        if not self.api_token:
            raise ValueError("BANKING_AUTH_KEY not configured in environment")
        
        # Remove trailing slash from base_url if present
        self.base_url = self.base_url.rstrip("/")
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a POST request to the API.
        
        Args:
            endpoint: API endpoint (e.g., "/branch/search")
            data: Request body data
            
        Returns:
            Response data as dictionary
            
        Raises:
            httpx.HTTPStatusError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        # Ensure ocode is always included in the payload
        payload = data or {}
        if "ocode" not in payload:
            payload["ocode"] = self.ocode
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    url,
                    json=payload,
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            error_msg = f"API request failed: {e.response.status_code} - {e.response.text}"
            raise Exception(error_msg) from e
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}") from e
    
    def get(self, endpoint: str) -> Any:
        """
        Make a GET request to the API.
        
        Args:
            endpoint: API endpoint (e.g., "/transaction/availableBalance/ocode/accountno")
            
        Returns:
            Response data
            
        Raises:
            httpx.HTTPStatusError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    url,
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            error_msg = f"API request failed: {e.response.status_code} - {e.response.text}"
            raise Exception(error_msg) from e
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}") from e
    
    def search_branches(self, filters: Optional[Dict[str, Any]] = None) -> list:
        """
        Search for branches.
        
        Args:
            filters: Optional filters (bcode, name, address, city, pin, status, etc.)
            
        Returns:
            List of branches
        """
        return self.post("/branch/search", filters)
    
    def search_deposit_schemes(self, filters: Optional[Dict[str, Any]] = None) -> list:
        """
        Search for deposit schemes.
        
        Args:
            filters: Optional filters (actype, name, tenure, interestrate, status, etc.)
            
        Returns:
            List of deposit schemes
        """
        return self.post("/depositscheme/search", filters)
    
    def search_loan_schemes(self, filters: Optional[Dict[str, Any]] = None) -> list:
        """
        Search for loan schemes.
        
        Args:
            filters: Optional filters (name, category, tenure, interestrate, status, etc.)
            
        Returns:
            List of loan schemes
        """
        return self.post("/loanscheme/search", filters)
    
    def search_members(self, filters: Optional[Dict[str, Any]] = None) -> list:
        """
        Search for members.
        
        Args:
            filters: Optional filters (memberno, name, gender, status, etc.)
            
        Returns:
            List of members
        """
        return self.post("/member/search", filters)
    
    def search_accounts(self, filters: Optional[Dict[str, Any]] = None) -> list:
        """
        Search for accounts.
        
        Args:
            filters: Optional filters (accountno, actype, memberno, status, etc.)
            
        Returns:
            List of accounts
        """
        return self.post("/account/search", filters)
    
    def search_transactions(self, filters: Optional[Dict[str, Any]] = None) -> list:
        """
        Search for transactions.
        
        Args:
            filters: Optional filters (transactionno, ttype, accountno, etc.)
            
        Returns:
            List of transactions
        """
        return self.post("/transaction/search", filters)
    
    def get_available_balance(self, ocode: str, accountno: str) -> dict:
        """
        Get available balance for an account.
        
        Args:
            ocode: Organization code
            accountno: Account number
            
        Returns:
            Dictionary with balance information (cbalance, tdate)
        """
        endpoint = f"/transaction/availableBalance/{ocode}/{accountno}"
        return self.get(endpoint)
