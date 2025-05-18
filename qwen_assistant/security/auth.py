"""
Authentication module for Qwen Multi-Assistant.

This module provides authentication functionality for the application,
including user authentication and MCP server authentication.
"""

import os
import time
import uuid
import logging
import hashlib
import hmac
from typing import Dict, Optional, Any, Tuple
from functools import wraps

logger = logging.getLogger(__name__)

class Auth:
    """
    Handles authentication for the Qwen Multi-Assistant application.
    
    This class provides:
    - Basic authentication mechanisms for API access
    - Session management for authenticated users
    - Token validation and rotation
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize the authentication manager.
        
        Args:
            secret_key: Secret key for token generation and validation.
                        If None, a random key will be generated (not persisted).
        """
        # Use provided secret key or generate a random one
        self._secret_key = secret_key or os.urandom(32).hex()
        self._sessions = {}  # session_id -> session_data
        
    def create_session(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Create a new authentication session.
        
        Args:
            user_id: Identifier for the user (default: "default")
            
        Returns:
            Session data including tokens and expiration
        """
        session_id = str(uuid.uuid4())
        created_at = int(time.time())
        expires_at = created_at + (24 * 60 * 60)  # 24 hours expiration
        
        # Create access token
        access_token = self._generate_token(session_id, user_id)
        
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "access_token": access_token,
            "created_at": created_at,
            "expires_at": expires_at,
            "active": True
        }
        
        self._sessions[session_id] = session
        return session
    
    def validate_token(self, access_token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate an access token and return the associated session.
        
        Args:
            access_token: The access token to validate
            
        Returns:
            Tuple of (is_valid, session_data or None)
        """
        # Parse token parts
        try:
            parts = access_token.split('.')
            if len(parts) != 3:
                return False, None
                
            session_id = parts[0]
            signature = parts[2]
            
            # Check if session exists
            if session_id not in self._sessions:
                return False, None
                
            session = self._sessions[session_id]
            
            # Check if session is expired or inactive
            if not session["active"] or int(time.time()) > session["expires_at"]:
                return False, None
                
            # Verify signature
            expected_token = self._generate_token(session_id, session["user_id"])
            if access_token != expected_token:
                return False, None
                
            return True, session
        except Exception as e:
            logger.warning(f"Token validation error: {e}")
            return False, None
    
    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a session.
        
        Args:
            session_id: The ID of the session to invalidate
            
        Returns:
            True if session was found and invalidated, False otherwise
        """
        if session_id in self._sessions:
            self._sessions[session_id]["active"] = False
            return True
        return False
    
    def _generate_token(self, session_id: str, user_id: str) -> str:
        """
        Generate a secure access token.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            
        Returns:
            Formatted access token
        """
        timestamp = str(int(time.time()))
        
        # Create payload part
        payload = f"{user_id}:{timestamp}"
        
        # Create signature
        payload_bytes = payload.encode('utf-8')
        signature = hmac.new(
            self._secret_key.encode('utf-8'),
            f"{session_id}.{payload}".encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Combine parts
        return f"{session_id}.{payload}.{signature}"


# Singleton auth instance
_auth_instance = None

def get_auth() -> Auth:
    """
    Get the singleton Auth instance.
    
    Returns:
        The shared Auth instance
    """
    global _auth_instance
    if _auth_instance is None:
        secret_key = os.environ.get("AUTH_SECRET_KEY")
        _auth_instance = Auth(secret_key)
    return _auth_instance


def require_auth(f):
    """
    Decorator to require authentication for a function.
    
    Args:
        f: The function to wrap
        
    Returns:
        Wrapped function that checks authentication
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = kwargs.pop('token', None)
        
        # For now, authentication is optional - this will be enhanced in future phases
        if token:
            auth = get_auth()
            is_valid, session = auth.validate_token(token)
            if not is_valid:
                raise ValueError("Invalid authentication token")
                
        return f(*args, **kwargs)
    return wrapped