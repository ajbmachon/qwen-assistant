"""
Tests for the data protection module.
"""

import json
import pytest

from qwen_assistant.security.data_protection import DataProtection, get_data_protection


class TestDataProtection:
    """Test suite for DataProtection."""
    
    def test_redact_text(self):
        """Test redacting sensitive information from text."""
        dp = DataProtection()
        
        # Test credit card redaction
        cc_text = "My credit card is 1234-5678-9012-3456."
        redacted = dp.redact_text(cc_text)
        assert "1234-5678-9012-3456" not in redacted
        assert "[REDACTED-CREDIT_CARD]" in redacted
        
        # Test SSN redaction
        ssn_text = "My SSN is 123-45-6789."
        redacted = dp.redact_text(ssn_text)
        assert "123-45-6789" not in redacted
        assert "[REDACTED-SSN]" in redacted
        
        # Test API key redaction
        api_key_text = "My API key is sk-1234567890abcdefghijklmn."
        redacted = dp.redact_text(api_key_text)
        assert "sk-1234567890abcdefghijklmn" not in redacted
        assert "[REDACTED-API_KEY]" in redacted
        
        # Test email redaction
        email_text = "Contact me at user@example.com."
        redacted = dp.redact_text(email_text)
        assert "user@example.com" not in redacted
        assert "[REDACTED-EMAIL]" in redacted
        
        # Test phone redaction
        phone_text = "Call me at (123) 456-7890."
        redacted = dp.redact_text(phone_text)
        assert "(123) 456-7890" not in redacted
        assert "[REDACTED-PHONE]" in redacted
        
        # Test multiple redactions in one text
        multi_text = "CC: 1234-5678-9012-3456, Email: user@example.com"
        redacted = dp.redact_text(multi_text)
        assert "1234-5678-9012-3456" not in redacted
        assert "user@example.com" not in redacted
        assert "[REDACTED-CREDIT_CARD]" in redacted
        assert "[REDACTED-EMAIL]" in redacted
        
        # Test empty text
        assert dp.redact_text("") == ""
        assert dp.redact_text(None) is None
    
    def test_clean_request_data(self):
        """Test cleaning a request data dictionary."""
        dp = DataProtection()
        
        # Test basic redaction of sensitive keys
        data = {
            "user": "test_user",
            "api_key": "sk-1234567890abcdef",
            "token": "secret_token_value",
            "query": "This is a test query"
        }
        
        cleaned = dp.clean_request_data(data)
        assert cleaned["user"] == "test_user"
        assert cleaned["api_key"] == "[REDACTED]"
        assert cleaned["token"] == "[REDACTED]"
        assert cleaned["query"] == "This is a test query"
        
        # Test nested dictionary
        nested_data = {
            "user": "test_user",
            "credentials": {
                "api_key": "sk-1234567890abcdef",
                "password": "secret123"
            },
            "settings": {
                "theme": "dark",
                "language": "en"
            }
        }
        
        cleaned = dp.clean_request_data(nested_data)
        assert cleaned["user"] == "test_user"
        assert cleaned["credentials"]["api_key"] == "[REDACTED]"
        assert cleaned["credentials"]["password"] == "[REDACTED]"
        assert cleaned["settings"]["theme"] == "dark"
        
        # Test with list values
        list_data = {
            "user": "test_user",
            "api_keys": ["key1", "key2", "key3"],
            "queries": ["query1", "query2"]
        }
        
        cleaned = dp.clean_request_data(list_data)
        assert cleaned["user"] == "test_user"
        assert cleaned["queries"] == ["query1", "query2"]
        
        # Test empty data
        assert dp.clean_request_data({}) == {}
        assert dp.clean_request_data(None) is None
    
    def test_sanitize_logs(self):
        """Test sanitizing log data."""
        dp = DataProtection()
        
        # Test string sanitization
        log_str = "API key: sk-1234567890abcdef, Phone: (123) 456-7890"
        sanitized = dp.sanitize_logs(log_str)
        assert "sk-1234567890abcdef" not in sanitized
        assert "(123) 456-7890" not in sanitized
        
        # Test dictionary sanitization
        log_dict = {
            "message": "User authentication",
            "data": {
                "user": "test_user",
                "email": "user@example.com",
                "credit_card": "1234-5678-9012-3456"
            }
        }
        
        sanitized = dp.sanitize_logs(log_dict)
        assert sanitized["message"] == "User authentication"
        assert "user@example.com" not in json.dumps(sanitized)
        assert "1234-5678-9012-3456" not in json.dumps(sanitized)
        
        # Test non-string/dict data is returned as is
        assert dp.sanitize_logs(123) == 123
        assert dp.sanitize_logs(True) is True


def test_get_data_protection_singleton():
    """Test that get_data_protection returns a singleton instance."""
    dp1 = get_data_protection()
    dp2 = get_data_protection()
    
    assert dp1 is dp2
