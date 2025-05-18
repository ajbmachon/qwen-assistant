"""
Tests for the central security manager.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from qwen_assistant.security.security_manager import SecurityManager, get_security_manager


class TestSecurityManager:
    """Test suite for SecurityManager."""
    
    @patch('qwen_assistant.security.api_keys.get_api_key_manager')
    @patch('qwen_assistant.security.auth.get_auth')
    @patch('qwen_assistant.security.data_protection.get_data_protection')
    @patch('qwen_assistant.security.validation.get_request_validator')
    @patch('qwen_assistant.security.validation.get_response_validator')
    @patch('qwen_assistant.security.logging.get_security_logger')
    def test_init(
        self, 
        mock_get_security_logger,
        mock_get_response_validator,
        mock_get_request_validator,
        mock_get_data_protection,
        mock_get_auth,
        mock_get_api_key_manager
    ):
        """Test initialization of the security manager."""
        # Setup mocks
        mock_api_key_manager = MagicMock()
        mock_auth = MagicMock()
        mock_data_protection = MagicMock()
        mock_request_validator = MagicMock()
        mock_response_validator = MagicMock()
        mock_security_logger = MagicMock()
        
        mock_get_api_key_manager.return_value = mock_api_key_manager
        mock_get_auth.return_value = mock_auth
        mock_get_data_protection.return_value = mock_data_protection
        mock_get_request_validator.return_value = mock_request_validator
        mock_get_response_validator.return_value = mock_response_validator
        mock_get_security_logger.return_value = mock_security_logger
        
        # Create security manager
        security_manager = SecurityManager()
        
        # Verify all components were initialized
        assert security_manager.api_key_manager is mock_api_key_manager
        assert security_manager.auth is mock_auth
        assert security_manager.data_protection is mock_data_protection
        assert security_manager.request_validator is mock_request_validator
        assert security_manager.response_validator is mock_response_validator
        assert security_manager.security_logger is mock_security_logger
    
    @patch('qwen_assistant.security.security_manager.get_api_key_manager')
    def test_validate_api_keys(self, mock_get_api_key_manager):
        """Test API key validation."""
        # Setup mocks
        mock_api_key_manager = MagicMock()
        mock_get_api_key_manager.return_value = mock_api_key_manager
        
        validation_results = {
            "OPENROUTER_API_KEY": {
                "present": True,
                "valid": True,
                "required": True,
                "description": "Main LLM API Key"
            },
            "MISSING_KEY": {
                "present": False,
                "valid": False,
                "required": True,
                "description": "Missing Key"
            }
        }
        mock_api_key_manager.validate_keys.return_value = validation_results
        
        # Create security manager with mocked components
        with patch('qwen_assistant.security.auth.get_auth'),\
             patch('qwen_assistant.security.data_protection.get_data_protection'),\
             patch('qwen_assistant.security.validation.get_request_validator'),\
             patch('qwen_assistant.security.validation.get_response_validator'),\
             patch('qwen_assistant.security.logging.get_security_logger'):
                 
            security_manager = SecurityManager()
            security_manager.security_logger = MagicMock()
            
            # Test validate_api_keys
            results = security_manager.validate_api_keys()
            
            # Verify API key manager was called
            mock_api_key_manager.validate_keys.assert_called_once()
            
            # Verify results are returned correctly
            assert results == validation_results
            
            # Verify logging of validation issues
            security_manager.security_logger.log_event.assert_called()
    
    @patch('qwen_assistant.security.security_manager.get_api_key_manager')
    def test_get_api_key(self, mock_get_api_key_manager):
        """Test getting an API key."""
        # Setup mocks
        mock_api_key_manager = MagicMock()
        mock_get_api_key_manager.return_value = mock_api_key_manager
        
        mock_api_key_manager.get_key.return_value = "test_api_key"
        mock_api_key_manager.get_masked_key.return_value = "test...key"
        
        # Create security manager with mocked components
        with patch('qwen_assistant.security.auth.get_auth'),\
             patch('qwen_assistant.security.data_protection.get_data_protection'),\
             patch('qwen_assistant.security.validation.get_request_validator'),\
             patch('qwen_assistant.security.validation.get_response_validator'),\
             patch('qwen_assistant.security.logging.get_security_logger'):
                 
            security_manager = SecurityManager()
            security_manager.security_logger = MagicMock()
            
            # Test get_api_key
            key = security_manager.get_api_key("TEST_KEY")
            
            # Verify API key manager was called
            mock_api_key_manager.get_key.assert_called_once_with("TEST_KEY")
            
            # Verify key is returned
            assert key == "test_api_key"
            
            # Verify logging of access
            security_manager.security_logger.log_access_event.assert_called_once()
    
    @patch('qwen_assistant.security.security_manager.get_auth')
    def test_create_session(self, mock_get_auth):
        """Test creating an authentication session."""
        # Setup mocks
        mock_auth = MagicMock()
        mock_get_auth.return_value = mock_auth
        
        mock_session = {
            "session_id": "test_session_id",
            "user_id": "test_user",
            "access_token": "test_token",
            "created_at": 1234567890,
            "expires_at": 1234654290,
            "active": True
        }
        mock_auth.create_session.return_value = mock_session
        
        # Create security manager with mocked components
        with patch('qwen_assistant.security.api_keys.get_api_key_manager'),\
             patch('qwen_assistant.security.data_protection.get_data_protection'),\
             patch('qwen_assistant.security.validation.get_request_validator'),\
             patch('qwen_assistant.security.validation.get_response_validator'),\
             patch('qwen_assistant.security.logging.get_security_logger'):
                 
            security_manager = SecurityManager()
            security_manager.security_logger = MagicMock()
            
            # Test create_session
            session = security_manager.create_session("test_user")
            
            # Verify auth was called
            mock_auth.create_session.assert_called_once_with("test_user")
            
            # Verify session is returned
            assert session == mock_session
            
            # Verify logging of session creation
            security_manager.security_logger.log_auth_event.assert_called_once()
    
    @patch('qwen_assistant.security.security_manager.get_auth')
    def test_validate_session(self, mock_get_auth):
        """Test validating an authentication session."""
        # Setup mocks
        mock_auth = MagicMock()
        mock_get_auth.return_value = mock_auth
        
        mock_session = {
            "session_id": "test_session_id",
            "user_id": "test_user",
            "created_at": 1234567890,
            "expires_at": 1234654290,
            "active": True
        }
        mock_auth.validate_token.return_value = (True, mock_session)
        
        # Create security manager with mocked components
        with patch('qwen_assistant.security.api_keys.get_api_key_manager'),\
             patch('qwen_assistant.security.data_protection.get_data_protection'),\
             patch('qwen_assistant.security.validation.get_request_validator'),\
             patch('qwen_assistant.security.validation.get_response_validator'),\
             patch('qwen_assistant.security.logging.get_security_logger'):
                 
            security_manager = SecurityManager()
            security_manager.security_logger = MagicMock()
            
            # Test validate_session with valid token
            is_valid, session = security_manager.validate_session("test_token")
            
            # Verify auth was called
            mock_auth.validate_token.assert_called_once_with("test_token")
            
            # Verify results are returned correctly
            assert is_valid is True
            assert session == mock_session
            
            # Verify logging of validation
            security_manager.security_logger.log_auth_event.assert_called_once()
    
    @patch('qwen_assistant.security.security_manager.get_request_validator')
    def test_validate_user_message(self, mock_get_request_validator):
        """Test validating a user message."""
        # Setup mocks
        mock_request_validator = MagicMock()
        mock_get_request_validator.return_value = mock_request_validator
        
        # Test valid message
        mock_request_validator.validate_user_message.return_value = (True, None)
        
        # Create security manager with mocked components
        with patch('qwen_assistant.security.api_keys.get_api_key_manager'),\
             patch('qwen_assistant.security.auth.get_auth'),\
             patch('qwen_assistant.security.data_protection.get_data_protection'),\
             patch('qwen_assistant.security.validation.get_response_validator'),\
             patch('qwen_assistant.security.logging.get_security_logger'):
                 
            security_manager = SecurityManager()
            security_manager.security_logger = MagicMock()
            
            # Test validate_user_message with valid message
            is_valid, error = security_manager.validate_user_message("Hello world")
            
            # Verify validator was called
            mock_request_validator.validate_user_message.assert_called_once_with("Hello world")
            
            # Verify results are returned correctly
            assert is_valid is True
            assert error is None
            
            # Security logger should not be called for valid messages
            security_manager.security_logger.log_security_violation.assert_not_called()
            
            # Test invalid message
            mock_request_validator.validate_user_message.reset_mock()
            mock_request_validator.validate_user_message.return_value = (False, "Invalid message")
            security_manager.security_logger.reset_mock()
            
            is_valid, error = security_manager.validate_user_message("Invalid message")
            
            # Verify results
            assert is_valid is False
            assert error == "Invalid message"
            
            # Verify security violation was logged
            security_manager.security_logger.log_security_violation.assert_called_once()


@patch('qwen_assistant.security.security_manager.SecurityManager')
def test_get_security_manager_singleton(mock_security_manager):
    """Test that get_security_manager returns a singleton instance."""
    mock_instance = MagicMock()
    mock_security_manager.return_value = mock_instance
    
    manager1 = get_security_manager()
    manager2 = get_security_manager()
    
    # Verify SecurityManager constructor was called only once
    mock_security_manager.assert_called_once()
    
    # Verify both calls return the same instance
    assert manager1 is manager2
    assert manager1 is mock_instance