"""
Tests for the authentication module.
"""

import os
import time
import pytest
from unittest.mock import patch, MagicMock

from qwen_assistant.security.auth import Auth, get_auth, require_auth


class TestAuth:
    """Test suite for Auth."""
    
    def test_create_session(self):
        """Test creating a new authentication session."""
        auth = Auth("test_secret_key")
        session = auth.create_session("test_user")
        
        assert session["user_id"] == "test_user"
        assert "session_id" in session
        assert "access_token" in session
        assert session["active"] is True
        assert session["expires_at"] > session["created_at"]
    
    def test_validate_token_valid(self):
        """Test validating a valid token."""
        auth = Auth("test_secret_key")
        session = auth.create_session("test_user")
        access_token = session["access_token"]
        
        is_valid, retrieved_session = auth.validate_token(access_token)
        
        assert is_valid is True
        assert retrieved_session is not None
        assert retrieved_session["session_id"] == session["session_id"]
        assert retrieved_session["user_id"] == "test_user"
    
    def test_validate_token_invalid(self):
        """Test validating an invalid token."""
        auth = Auth("test_secret_key")
        
        # Test completely invalid token
        is_valid, session = auth.validate_token("invalid_token")
        assert is_valid is False
        assert session is None
        
        # Test malformed token
        is_valid, session = auth.validate_token("part1.part2")
        assert is_valid is False
        assert session is None
        
        # Test invalid signature
        session = auth.create_session("test_user")
        parts = session["access_token"].split('.')
        tampered_token = f"{parts[0]}.{parts[1]}.invalid_signature"
        
        is_valid, session = auth.validate_token(tampered_token)
        assert is_valid is False
        assert session is None
    
    def test_invalidate_session(self):
        """Test invalidating a session."""
        auth = Auth("test_secret_key")
        session = auth.create_session("test_user")
        
        # Validate session is active
        is_valid, _ = auth.validate_token(session["access_token"])
        assert is_valid is True
        
        # Invalidate session
        result = auth.invalidate_session(session["session_id"])
        assert result is True
        
        # Validate session is no longer active
        is_valid, _ = auth.validate_token(session["access_token"])
        assert is_valid is False
        
        # Try to invalidate non-existent session
        result = auth.invalidate_session("nonexistent_session_id")
        assert result is False
    
    def test_token_expiration(self):
        """Test token expiration."""
        auth = Auth("test_secret_key")
        session = auth.create_session("test_user")
        
        # Manually expire the session
        session_id = session["session_id"]
        auth._sessions[session_id]["expires_at"] = int(time.time()) - 1
        
        # Verify token is invalid due to expiration
        is_valid, _ = auth.validate_token(session["access_token"])
        assert is_valid is False


def test_get_auth_singleton():
    """Test that get_auth returns a singleton instance."""
    with patch('os.environ.get', return_value="test_secret_key"):
        auth1 = get_auth()
        auth2 = get_auth()
        
        assert auth1 is auth2


def test_require_auth_decorator():
    """Test the require_auth decorator."""
    auth = Auth("test_secret_key")
    session = auth.create_session("test_user")
    access_token = session["access_token"]
    
    with patch('qwen_assistant.security.auth.get_auth', return_value=auth):
        # Create a decorated function
        @require_auth
        def test_function(param1, param2, token=None):
            return param1 + param2
        
        # Test with valid token
        result = test_function(1, 2, token=access_token)
        assert result == 3
        
        # Test without token (should still work as auth is optional in MVP)
        result = test_function(3, 4)
        assert result == 7
        
        # Test with invalid token
        with pytest.raises(ValueError):
            test_function(5, 6, token="invalid_token")