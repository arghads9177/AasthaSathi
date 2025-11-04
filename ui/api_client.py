"""
API Client for AasthaSathi Backend
Handles communication with the AasthaSathi REST API and MyAastha login API.
"""

import requests
from typing import Dict, Any, Optional, Tuple
from requests.auth import HTTPBasicAuth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MyAasthaAuthError(Exception):
    """Raised when MyAastha authentication fails"""
    pass


class AasthaSathiAPIError(Exception):
    """Raised when AasthaSathi API request fails"""
    pass


class AasthaSathiAPIClient:
    """
    Client wrapper for AasthaSathi REST API.
    
    Handles:
    - MyAastha user authentication
    - AasthaSathi API queries with Basic Auth
    - Health checks and connection management
    - Error handling and timeout management
    """
    
    def __init__(
        self,
        api_base_url: str,
        api_username: str,
        api_password: str,
        myaastha_login_url: str,
        myaastha_auth_token: str = None,
        timeout: int = 30
    ):
        """
        Initialize API client.
        
        Args:
            api_base_url: Base URL for AasthaSathi API (e.g., http://localhost:8000)
            api_username: Username for AasthaSathi API Basic Auth
            api_password: Password for AasthaSathi API Basic Auth
            myaastha_login_url: URL for MyAastha login API
            myaastha_auth_token: Bearer token for MyAastha API authorization
            timeout: Request timeout in seconds
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.api_username = api_username
        self.api_password = api_password
        self.myaastha_login_url = myaastha_login_url
        self.myaastha_auth_token = myaastha_auth_token
        self.timeout = timeout
        
        # Create Basic Auth object for AasthaSathi API
        self.auth = HTTPBasicAuth(api_username, api_password)
        
        # Store user session info
        self.user_info: Optional[Dict[str, Any]] = None
        self.is_authenticated: bool = False
        
        logger.info(f"Initialized AasthaSathi API Client: {api_base_url}")
    
    def login_myaastha(self, userid: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Authenticate user with MyAastha login API.
        
        Args:
            userid: MyAastha user ID
            password: User password
            
        Returns:
            Tuple of (success: bool, user_data: dict or None, error_message: str or None)
            
        MyAastha API returns user object directly on successful login with fields:
        - _id, userid, firstname, lastname, mobile, email, role, status
        - usertoken (JWT token for authenticated requests)
        - imageUrl (profile picture URL)
        - ocode (organization code)
        """
        try:
            logger.info(f"Attempting MyAastha login for user: {userid}")
            
            # Prepare headers with authorization token
            headers = {}
            if self.myaastha_auth_token:
                headers["Authorization"] = self.myaastha_auth_token
            
            response = requests.post(
                self.myaastha_login_url,
                json={"userid": userid, "password": password},
                headers=headers,
                timeout=self.timeout
            )
            
            # Check if request was successful
            if response.status_code == 200:
                user_data = response.json()
                
                # MyAastha API returns user object directly on success
                # Check for required fields to verify successful login
                if user_data.get("userid") and user_data.get("usertoken"):
                    # Store user information
                    self.user_info = {
                        "id": user_data.get("_id"),
                        "userid": user_data.get("userid"),
                        "name": f"{user_data.get('firstname', '')} {user_data.get('lastname', '')}".strip(),
                        "firstname": user_data.get("firstname"),
                        "lastname": user_data.get("lastname"),
                        "mobile": user_data.get("mobile"),
                        "email": user_data.get("email"),
                        "role": user_data.get("role"),
                        "status": user_data.get("status"),
                        "ocode": user_data.get("ocode"),
                        "usertoken": user_data.get("usertoken"),
                        "imageUrl": user_data.get("imageUrl"),
                        "userat": user_data.get("userat")
                    }
                    self.is_authenticated = True
                    logger.info(f"MyAastha login successful for user: {userid} ({self.user_info['name']})")
                    return True, self.user_info, None
                else:
                    # Login failed - missing required fields
                    error_msg = user_data.get("message", "Invalid credentials")
                    logger.warning(f"MyAastha login failed: {error_msg}")
                    return False, None, error_msg
            elif response.status_code == 404:
                # Authentication failure - incorrect userid or password
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "The userid or password you entered is incorrect")
                except:
                    error_msg = "The userid or password you entered is incorrect"
                logger.warning(f"MyAastha login failed (404): {error_msg}")
                return False, None, error_msg
            elif response.status_code == 401:
                error_msg = "Invalid username or password"
                logger.warning(f"MyAastha login failed: {error_msg}")
                return False, None, error_msg
            else:
                # Handle other error status codes
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", error_data.get("message", f"Login failed with status {response.status_code}"))
                except:
                    error_msg = f"Login failed with status {response.status_code}"
                logger.error(error_msg)
                return False, None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Login request timed out"
            logger.error(error_msg)
            return False, None, error_msg
        except requests.exceptions.ConnectionError:
            error_msg = "Could not connect to MyAastha server"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Login error: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def logout(self):
        """Clear user session data."""
        self.user_info = None
        self.is_authenticated = False
        logger.info("User logged out")
    
    def health_check(self) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Check if AasthaSathi API is healthy and accessible.
        
        Returns:
            Tuple of (is_healthy: bool, health_data: dict or None, error_message: str or None)
        """
        try:
            url = f"{self.api_base_url}/api/v1/health"
            logger.info(f"Health check: {url}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Health check successful")
                return True, data, None
            else:
                error_msg = f"Health check failed with status {response.status_code}"
                logger.warning(error_msg)
                return False, None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Health check timed out"
            logger.error(error_msg)
            return False, None, error_msg
        except requests.exceptions.ConnectionError:
            error_msg = "Could not connect to AasthaSathi API"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Health check error: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def query(
        self,
        question: str,
        query_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Submit a query to AasthaSathi API.
        
        Args:
            question: The user's question
            query_type: Optional query type hint ('api', 'rag', 'hybrid')
            metadata: Optional metadata to include with query
            
        Returns:
            Tuple of (success: bool, response_data: dict or None, error_message: str or None)
        """
        try:
            url = f"{self.api_base_url}/api/v1/query"
            
            # Build request payload - API expects 'query' not 'question'
            payload = {
                "query": question,
                "include_sources": True,
                "include_metadata": True
            }
            
            # Note: query_type and metadata are not part of the API schema
            # The API will auto-detect the query type based on content
            
            logger.info(f"Submitting query to: {url}")
            logger.debug(f"Query payload: {payload}")
            
            # Make authenticated request
            response = requests.post(
                url,
                json=payload,
                auth=self.auth,
                timeout=self.timeout
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                logger.info("Query successful")
                return True, data, None
            elif response.status_code == 401:
                error_msg = "Authentication failed - Invalid API credentials"
                logger.error(error_msg)
                return False, None, error_msg
            else:
                error_msg = f"Query failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return False, None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = f"Query timed out after {self.timeout} seconds"
            logger.error(error_msg)
            return False, None, error_msg
        except requests.exceptions.ConnectionError:
            error_msg = "Could not connect to AasthaSathi API"
            logger.error(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Query error: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get comprehensive connection status.
        
        Returns:
            Dictionary with connection status information
        """
        is_healthy, health_data, error = self.health_check()
        
        return {
            "api_connected": is_healthy,
            "api_url": self.api_base_url,
            "user_authenticated": self.is_authenticated,
            "user_info": self.user_info,
            "health_data": health_data,
            "error": error
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration (would come from config.py in actual app)
    from config import (
        AASTHASATHI_API_URL,
        AASTHASATHI_API_USERNAME,
        AASTHASATHI_API_PASSWORD,
        MYAASTHA_LOGIN_URL,
        MYAASTHA_AUTH_TOKEN
    )
    
    # Initialize client
    client = AasthaSathiAPIClient(
        api_base_url=AASTHASATHI_API_URL,
        api_username=AASTHASATHI_API_USERNAME,
        api_password=AASTHASATHI_API_PASSWORD,
        myaastha_login_url=MYAASTHA_LOGIN_URL,
        myaastha_auth_token=MYAASTHA_AUTH_TOKEN
    )
    
    # Test health check
    print("\n=== Testing Health Check ===")
    is_healthy, health_data, error = client.health_check()
    if is_healthy:
        print(f"✓ API is healthy: {health_data}")
    else:
        print(f"✗ Health check failed: {error}")
    
    # Test query (requires API to be running)
    print("\n=== Testing Query ===")
    success, response, error = client.query("What is MyAastha?")
    if success:
        print(f"✓ Query successful")
        print(f"Response: {response.get('answer', 'N/A')}")
    else:
        print(f"✗ Query failed: {error}")
    
    # Test connection status
    print("\n=== Connection Status ===")
    status = client.get_connection_status()
    for key, value in status.items():
        print(f"{key}: {value}")
