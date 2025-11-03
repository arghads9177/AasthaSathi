"""
Authentication middleware for AasthaSathi API.

Implements HTTP Basic Authentication for API endpoints.
"""

import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from core.config import get_settings

# Initialize HTTPBasic security scheme
security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Verify HTTP Basic Authentication credentials.
    
    Args:
        credentials: HTTPBasicCredentials from Authorization header
        
    Returns:
        username if authentication successful
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    settings = get_settings()
    
    # Get expected credentials from environment
    correct_username = settings.api_username
    correct_password = settings.api_password
    
    # Use secrets.compare_digest to prevent timing attacks
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"),
        correct_username.encode("utf8")
    )
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"),
        correct_password.encode("utf8")
    )
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username


# Dependency for protected endpoints
def get_current_user(username: str = Depends(verify_credentials)) -> str:
    """
    Get the current authenticated user.
    
    This is a convenience dependency that can be used in endpoints
    to get the authenticated username.
    
    Args:
        username: Verified username from verify_credentials
        
    Returns:
        username string
    """
    return username
