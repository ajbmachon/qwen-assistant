"""
Tests for the request and response validation module.
"""

import pytest

from qwen_assistant.security.validation import (
    RequestValidator, 
    ResponseValidator,
    get_request_validator,
    get_response_validator
)


class TestRequestValidator:
    """Test suite for RequestValidator."""
    
    def test_validate_user_message(self):
        """Test validating user messages."""
        validator = RequestValidator(max_message_length=100)
        
        # Test valid message
        is_valid, error = validator.validate_user_message("This is a valid message")
        assert is_valid is True
        assert error is None
        
        # Test empty message
        is_valid, error = validator.validate_user_message("")
        assert is_valid is False
        assert "empty" in error.lower()
        
        # Test message exceeding max length
        long_message = "x" * 101
        is_valid, error = validator.validate_user_message(long_message)
        assert is_valid is False
        assert "maximum length" in error.lower()
        
        # Test message with potentially malicious content
        malicious_message = "Normal text <script>alert('XSS')</script> more text"
        is_valid, error = validator.validate_user_message(malicious_message)
        assert is_valid is False
        assert "harmful content" in error.lower()
    
    def test_validate_tool_parameters(self):
        """Test validating tool parameters."""
        validator = RequestValidator()
        
        # Test valid parameters
        is_valid, error = validator.validate_tool_parameters(
            "test_tool", 
            {"param1": "value1", "param2": 123}
        )
        assert is_valid is True
        assert error is None
        
        # Test empty tool name
        is_valid, error = validator.validate_tool_parameters(
            "", 
            {"param1": "value1"}
        )
        assert is_valid is False
        assert "tool name" in error.lower()
        
        # Test non-dict parameters
        is_valid, error = validator.validate_tool_parameters(
            "test_tool", 
            "not_a_dict"
        )
        assert is_valid is False
        assert "must be a dictionary" in error.lower()
        
        # Test parameters with malicious content
        is_valid, error = validator.validate_tool_parameters(
            "test_tool", 
            {"param1": "<script>alert('XSS')</script>"}
        )
        assert is_valid is False
        assert "harmful content" in error.lower()
    
    def test_sanitize_input(self):
        """Test sanitizing input data."""
        validator = RequestValidator()
        
        # Test sanitizing string
        malicious_str = "Text with <script>alert('XSS')</script> script"
        sanitized = validator.sanitize_input(malicious_str)
        assert "<script>" not in sanitized
        assert "[REMOVED]" in sanitized
        
        # Test sanitizing dictionary
        malicious_dict = {
            "param1": "normal value",
            "param2": "value with <script>alert('XSS')</script>",
            "nested": {
                "param3": "another <script> tag"
            }
        }
        
        sanitized = validator.sanitize_input(malicious_dict)
        assert "<script>" not in sanitized["param2"]
        assert "[REMOVED]" in sanitized["param2"]
        assert "<script>" not in sanitized["nested"]["param3"]
        
        # Test sanitizing list
        malicious_list = [
            "normal value",
            "value with <script>alert('XSS')</script>",
            {"nested": "another <script> tag"}
        ]
        
        sanitized = validator.sanitize_input(malicious_list)
        assert "<script>" not in sanitized[1]
        assert "[REMOVED]" in sanitized[1]
        assert "<script>" not in sanitized[2]["nested"]
        
        # Test sanitizing non-string, non-container values
        assert validator.sanitize_input(123) == 123
        assert validator.sanitize_input(True) is True
        assert validator.sanitize_input(None) is None


class TestResponseValidator:
    """Test suite for ResponseValidator."""
    
    def test_validate_agent_response(self):
        """Test validating agent responses."""
        validator = ResponseValidator()
        
        # Test valid response
        valid_response = {
            "message": "This is a valid response",
            "tools": ["tool1", "tool2"]
        }
        
        is_valid, error = validator.validate_agent_response(valid_response)
        assert is_valid is True
        assert error is None
        
        # Test non-dict response
        is_valid, error = validator.validate_agent_response("not a dict")
        assert is_valid is False
        assert "must be a dictionary" in error.lower()
        
        # Test missing required field
        invalid_response = {
            "tools": ["tool1", "tool2"]
        }
        
        is_valid, error = validator.validate_agent_response(invalid_response)
        assert is_valid is False
        assert "missing required field" in error.lower()
        
        # Test extremely large message
        large_response = {
            "message": "x" * 100001
        }
        
        is_valid, error = validator.validate_agent_response(large_response)
        assert is_valid is False
        assert "too large" in error.lower()
    
    def test_sanitize_error_messages(self):
        """Test sanitizing error messages."""
        validator = ResponseValidator()
        
        # Test sanitizing error with password
        error_with_password = "Failed to connect: password='secret123', host='example.com'"
        sanitized = validator.sanitize_error_messages(error_with_password)
        assert "password='secret123'" not in sanitized
        assert "password=[REDACTED]" in sanitized
        assert "host='example.com'" in sanitized
        
        # Test sanitizing error with API key
        error_with_key = 'Error: Invalid key="sk_1234567890abcdef"'
        sanitized = validator.sanitize_error_messages(error_with_key)
        assert 'key="sk_1234567890abcdef"' not in sanitized
        assert 'key=[REDACTED]' in sanitized
        
        # Test sanitizing connection string
        error_with_conn = "Failed to connect: ConnectionString=Server=myserver;Database=mydb;User=myuser;Password=mypass;"
        sanitized = validator.sanitize_error_messages(error_with_conn)
        assert "Password=mypass" not in sanitized
        assert "ConnectionString=[REDACTED]" in sanitized
    
    def test_prepare_safe_response(self):
        """Test preparing safe responses."""
        validator = ResponseValidator()
        
        # Test successful response with data
        data = {
            "message": "Operation successful",
            "results": [1, 2, 3],
            "_internal": "Should be removed",
            "internal": "Should also be removed"
        }
        
        response = validator.prepare_safe_response(True, data)
        assert response["success"] is True
        assert "data" in response
        assert response["data"]["message"] == "Operation successful"
        assert response["data"]["results"] == [1, 2, 3]
        assert "_internal" not in response["data"]
        assert "internal" not in response["data"]
        
        # Test error response
        response = validator.prepare_safe_response(False, error="Something went wrong")
        assert response["success"] is False
        assert "data" not in response
        assert response["error"] == "Something went wrong"
        
        # Test error response with sensitive information
        response = validator.prepare_safe_response(
            False, 
            error="Failed with password='secret123'"
        )
        assert "password='secret123'" not in response["error"]
        assert "password=[REDACTED]" in response["error"]
    
    def test_remove_internal_fields(self):
        """Test removing internal fields."""
        validator = ResponseValidator()
        
        # Test with dictionary
        data = {
            "public": "visible",
            "_private": "hidden",
            "internal": "hidden",
            "nested": {
                "public": "visible",
                "_private": "hidden",
                "list": [
                    {"public": "visible", "_private": "hidden"},
                    {"internal": "hidden"}
                ]
            }
        }
        
        cleaned = validator._remove_internal_fields(data)
        assert "public" in cleaned
        assert "_private" not in cleaned
        assert "internal" not in cleaned
        assert "nested" in cleaned
        assert "public" in cleaned["nested"]
        assert "_private" not in cleaned["nested"]
        assert "_private" not in cleaned["nested"]["list"][0]
        assert "internal" not in cleaned["nested"]["list"][1]
        
        # Test with list
        data = [
            {"public": "visible", "_private": "hidden"},
            {"internal": "hidden"}
        ]
        
        cleaned = validator._remove_internal_fields(data)
        assert len(cleaned) == 2
        assert "public" in cleaned[0]
        assert "_private" not in cleaned[0]
        assert "internal" not in cleaned[1]
        
        # Test with primitive values
        assert validator._remove_internal_fields(123) == 123
        assert validator._remove_internal_fields("string") == "string"
        assert validator._remove_internal_fields(True) is True


def test_get_request_validator_singleton():
    """Test that get_request_validator returns a singleton instance."""
    validator1 = get_request_validator()
    validator2 = get_request_validator()
    
    assert validator1 is validator2


def test_get_response_validator_singleton():
    """Test that get_response_validator returns a singleton instance."""
    validator1 = get_response_validator()
    validator2 = get_response_validator()
    
    assert validator1 is validator2
