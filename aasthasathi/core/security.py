"""
Security utilities for AasthaSathi

Handles authentication, authorization, and security-related functions.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from fastapi import HTTPException, status

from .config import get_settings
from .models import User, UserRole


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def check_permissions(user_role: UserRole, required_permission: str) -> bool:
    """Check if user role has required permission."""
    
    # Define role-based permissions
    role_permissions = {
        UserRole.ADMIN: [
            "read_all_accounts",
            "read_policies", 
            "system_admin",
            "audit_logs",
            "user_management"
        ],
        UserRole.EMPLOYEE: [
            "read_all_accounts",
            "read_policies",
            "process_transactions"
        ],
        UserRole.AGENT: [
            "read_limited_accounts",
            "read_policies"
        ],
        UserRole.PUBLIC: [
            "read_policies"
        ]
    }
    
    user_permissions = role_permissions.get(user_role, [])
    return required_permission in user_permissions


def sanitize_member_data(data: dict, user_role: UserRole) -> dict:
    """Sanitize member data based on user role."""
    
    # Full access for admin and employees
    if user_role in [UserRole.ADMIN, UserRole.EMPLOYEE]:
        return data
    
    # Limited access for agents
    elif user_role == UserRole.AGENT:
        # Remove sensitive fields
        sensitive_fields = ["ssn", "phone", "email", "address"]
        return {k: v for k, v in data.items() if k not in sensitive_fields}
    
    # No access for public users
    else:
        return {}


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = {}
        self.settings = get_settings()
    
    def is_allowed(self, user_id: str) -> bool:
        """Check if user is within rate limits."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.settings.rate_limit_period)
        
        # Clean old entries
        if user_id in self.requests:
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id] 
                if req_time > window_start
            ]
        else:
            self.requests[user_id] = []
        
        # Check if under limit
        if len(self.requests[user_id]) < self.settings.rate_limit_requests:
            self.requests[user_id].append(now)
            return True
        
        return False


# Global rate limiter instance
rate_limiter = RateLimiter()