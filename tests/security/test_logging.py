"""
Tests for the security logging module.
"""

import json
import logging
import os
import pytest
from unittest.mock import patch, MagicMock, ANY

from qwen_assistant.security.logging import SecurityLogger, get_security_logger


class TestSecurityLogger:
    """Test suite for SecurityLogger."""
    
    @patch('qwen_assistant.security.logging.get_data_protection')
    def test_init(self, mock_get_data_protection):
        """Test initialization of the security logger."""
        # Setup mocks
        mock_data_protection = MagicMock()
        mock_get_data_protection.return_value = mock_data_protection
        
        # Create logger without log_dir
        logger = SecurityLogger()
        
        # Verify data protection was initialized
        assert logger.data_protection is mock_data_protection
        assert logger.log_dir is None
        
        # Create logger with log_dir
        with patch('os.makedirs') as mock_makedirs:
            logger = SecurityLogger(log_dir="/test/logs")
            
            # Verify log directory was created
            mock_makedirs.assert_called_once_with("/test/logs", exist_ok=True)
            assert logger.log_dir == "/test/logs"
    
    @patch('qwen_assistant.security.logging.get_data_protection')
    @patch('logging.Logger.log')
    def test_log_event(self, mock_log, mock_get_data_protection):
        """Test logging a security event."""
        # Setup mocks
        mock_data_protection = MagicMock()
        mock_get_data_protection.return_value = mock_data_protection
        
        # Create logger
        logger = SecurityLogger()
        
        # Test log_event
        logger.log_event(
            event_type="authentication",
            message="User logged in",
            details={"ip": "192.168.1.1"},
            user_id="test_user",
            severity="INFO"
        )
        
        # Verify logging
        mock_log.assert_called_once()
        
        # Verify log level
        assert mock_log.call_args[0][0] == logging.INFO
        
        # Extract logged message
        log_message = mock_log.call_args[0][1]
        log_data = json.loads(log_message)
        
        # Verify event data
        assert log_data["event_type"] == "authentication"
        assert log_data["event_code"] == "AUTH"
        assert log_data["message"] == "User logged in"
        assert log_data["user_id"] == "test_user"
        assert "timestamp" in log_data
        assert "event_id" in log_data
        assert "details" in log_data
        
        # Verify data sanitization was used
        mock_data_protection.sanitize_logs.assert_called_once_with({"ip": "192.168.1.1"})
    
    @patch('qwen_assistant.security.logging.get_data_protection')
    def test_log_auth_event(self, mock_get_data_protection):
        """Test logging an authentication event."""
        # Setup mocks
        mock_data_protection = MagicMock()
        mock_get_data_protection.return_value = mock_data_protection
        
        # Create logger with a mocked log_event method
        logger = SecurityLogger()
        logger.log_event = MagicMock()
        
        # Test successful authentication
        logger.log_auth_event(
            message="User logged in successfully",
            user_id="test_user",
            success=True,
            details={"method": "password"}
        )
        
        # Verify log_event was called with correct parameters
        logger.log_event.assert_called_once_with(
            event_type="authentication",
            message="User logged in successfully",
            details={"method": "password"},
            user_id="test_user",
            severity="INFO"
        )
        
        # Reset mock and test failed authentication
        logger.log_event.reset_mock()
        logger.log_auth_event(
            message="Login failed: invalid password",
            user_id="test_user",
            success=False,
            details={"method": "password", "attempts": 3}
        )
        
        # Verify log_event was called with correct parameters
        logger.log_event.assert_called_once_with(
            event_type="authentication",
            message="Login failed: invalid password",
            details={"method": "password", "attempts": 3},
            user_id="test_user",
            severity="WARNING"
        )
    
    @patch('qwen_assistant.security.logging.get_data_protection')
    def test_log_access_event(self, mock_get_data_protection):
        """Test logging a resource access event."""
        # Setup mocks
        mock_data_protection = MagicMock()
        mock_get_data_protection.return_value = mock_data_protection
        
        # Create logger with a mocked log_event method
        logger = SecurityLogger()
        logger.log_event = MagicMock()
        
        # Test successful access
        logger.log_access_event(
            resource="document:123",
            action="read",
            user_id="test_user",
            success=True,
            details={"reason": "document view"}
        )
        
        # Verify log_event was called with correct parameters
        logger.log_event.assert_called_once_with(
            event_type="authorization",
            message="Resource access: read on document:123",
            details={"reason": "document view"},
            user_id="test_user",
            severity="INFO"
        )
        
        # Reset mock and test failed access
        logger.log_event.reset_mock()
        logger.log_access_event(
            resource="admin:settings",
            action="write",
            user_id="test_user",
            success=False,
            details={"reason": "insufficient permissions"}
        )
        
        # Verify log_event was called with correct parameters
        logger.log_event.assert_called_once_with(
            event_type="authorization",
            message="Resource access: write on admin:settings",
            details={"reason": "insufficient permissions"},
            user_id="test_user",
            severity="WARNING"
        )
    
    @patch('qwen_assistant.security.logging.get_data_protection')
    def test_log_api_request(self, mock_get_data_protection):
        """Test logging an API request."""
        # Setup mocks
        mock_data_protection = MagicMock()
        mock_get_data_protection.return_value = mock_data_protection
        
        # Create logger with a mocked log_event method
        logger = SecurityLogger()
        logger.log_event = MagicMock()
        
        # Test successful request (2xx)
        logger.log_api_request(
            endpoint="/api/resource",
            method="GET",
            user_id="test_user",
            status_code=200,
            details={"query": "param=value"}
        )
        
        # Verify log_event was called with correct parameters
        logger.log_event.assert_called_once_with(
            event_type="api_request",
            message="GET /api/resource (Status: 200)",
            details={"query": "param=value"},
            user_id="test_user",
            severity="INFO"
        )
        
        # Reset mock and test client error (4xx)
        logger.log_event.reset_mock()
        logger.log_api_request(
            endpoint="/api/resource",
            method="POST",
            user_id="test_user",
            status_code=404,
            details={"error": "Resource not found"}
        )
        
        # Verify log_event was called with correct parameters
        logger.log_event.assert_called_once_with(
            event_type="api_request",
            message="POST /api/resource (Status: 404)",
            details={"error": "Resource not found"},
            user_id="test_user",
            severity="WARNING"
        )
        
        # Reset mock and test server error (5xx)
        logger.log_event.reset_mock()
        logger.log_api_request(
            endpoint="/api/resource",
            method="PUT",
            user_id="test_user",
            status_code=500,
            details={"error": "Internal server error"}
        )
        
        # Verify log_event was called with correct parameters
        logger.log_event.assert_called_once_with(
            event_type="api_request",
            message="PUT /api/resource (Status: 500)",
            details={"error": "Internal server error"},
            user_id="test_user",
            severity="ERROR"
        )
    
    @patch('qwen_assistant.security.logging.get_data_protection')
    def test_log_security_violation(self, mock_get_data_protection):
        """Test logging a security violation."""
        # Setup mocks
        mock_data_protection = MagicMock()
        mock_get_data_protection.return_value = mock_data_protection
        
        # Create logger with a mocked log_event method
        logger = SecurityLogger()
        logger.log_event = MagicMock()
        
        # Test logging a security violation
        logger.log_security_violation(
            violation_type="input_validation",
            message="Potentially malicious input detected",
            user_id="test_user",
            details={"input": "<script>alert('XSS')</script>"}
        )
        
        # Verify log_event was called with correct parameters
        logger.log_event.assert_called_once_with(
            event_type="security_violation",
            message="input_validation: Potentially malicious input detected",
            details={"input": "<script>alert('XSS')</script>"},
            user_id="test_user",
            severity="WARNING"
        )
    
    @patch('qwen_assistant.security.logging.get_data_protection')
    def test_log_tool_usage(self, mock_get_data_protection):
        """Test logging tool usage."""
        # Setup mocks
        mock_data_protection = MagicMock()
        mock_get_data_protection.return_value = mock_data_protection
        
        # Create logger with a mocked log_event method
        logger = SecurityLogger()
        logger.log_event = MagicMock()
        
        # Test successful tool usage
        logger.log_tool_usage(
            tool_name="search_tool",
            action="search",
            user_id="test_user",
            success=True,
            details={"query": "test query"}
        )
        
        # Verify log_event was called with correct parameters
        logger.log_event.assert_called_once_with(
            event_type="tool_usage",
            message="Tool usage: search_tool search",
            details={"query": "test query"},
            user_id="test_user",
            severity="INFO"
        )
        
        # Reset mock and test failed tool usage
        logger.log_event.reset_mock()
        logger.log_tool_usage(
            tool_name="file_tool",
            action="read",
            user_id="test_user",
            success=False,
            details={"path": "/etc/passwd", "error": "Permission denied"}
        )
        
        # Verify log_event was called with correct parameters
        logger.log_event.assert_called_once_with(
            event_type="tool_usage",
            message="Tool usage: file_tool read",
            details={"path": "/etc/passwd", "error": "Permission denied"},
            user_id="test_user",
            severity="WARNING"
        )


@patch('qwen_assistant.security.logging.SecurityLogger')
def test_get_security_logger_singleton(mock_security_logger):
    """Test that get_security_logger returns a singleton instance."""
    mock_instance = MagicMock()
    mock_security_logger.return_value = mock_instance
    
    logger1 = get_security_logger()
    logger2 = get_security_logger()
    
    # Verify SecurityLogger constructor was called only once
    mock_security_logger.assert_called_once_with(None)
    
    # Verify both calls return the same instance
    assert logger1 is logger2
    assert logger1 is mock_instance
    
    # Test with log_dir
    mock_security_logger.reset_mock()
    mock_security_logger.return_value = MagicMock()
    
    # This shouldn't create a new instance since we're using a singleton
    logger3 = get_security_logger(log_dir="/test/logs")
    
    # Verify constructor wasn't called again
    mock_security_logger.assert_not_called()
    
    # Verify we got the same instance as before
    assert logger3 is logger1
