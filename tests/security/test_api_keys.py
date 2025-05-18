"""
Tests for the API key management module.
"""

import os
import pytest
from unittest.mock import patch

from qwen_assistant.security.api_keys import ApiKeyManager, get_api_key_manager


class TestApiKeyManager:
    """Test suite for ApiKeyManager."""
    
    def test_load_from_env(self):
        """Test loading API keys from environment variables."""
        test_key = "test_api_key_value"
        
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": test_key}):
            manager = ApiKeyManager()
            assert manager.get_key("OPENROUTER_API_KEY") == test_key
    
    def test_validate_keys(self):
        """Test key validation."""
        with patch.dict(os.environ, {
            "OPENROUTER_API_KEY": "sk-or-abcdefghijklmnopqrstuvwx",
            "EXA_API_KEY": "exa-abcdefghijklmnopqrstuvwxyz123456",
            "AIRTABLE_API_KEY": "patInvalidFormatKey",
        }):
            manager = ApiKeyManager()
            validation = manager.validate_keys()
            
            # Check OPENROUTER_API_KEY validation
            assert validation["OPENROUTER_API_KEY"]["present"] is True
            assert validation["OPENROUTER_API_KEY"]["valid"] is True
            
            # Check EXA_API_KEY validation
            assert validation["EXA_API_KEY"]["present"] is True
            assert validation["EXA_API_KEY"]["valid"] is True
            
            # Check AIRTABLE_API_KEY validation (invalid format)
            assert validation["AIRTABLE_API_KEY"]["present"] is True
            assert validation["AIRTABLE_API_KEY"]["valid"] is False
    
    def test_missing_required_keys(self):
        """Test detection of missing required keys."""
        # No keys in environment
        with patch.dict(os.environ, {}, clear=True):
            manager = ApiKeyManager()
            assert manager.missing_required_keys is True
    
    def test_mask_key(self):
        """Test API key masking."""
        manager = ApiKeyManager()
        
        # Test short key
        short_key = "1234"
        assert manager.mask_key(short_key) == "****"
        
        # Test normal key
        normal_key = "abcdefghijklmnopqrstuvwxyz"
        masked = manager.mask_key(normal_key)
        assert masked == "abcd...wxyz"
        assert len(masked) < len(normal_key)
        
        # Test empty key
        assert manager.mask_key("") == ""
    
    def test_get_masked_key(self):
        """Test getting a masked key."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-abcdefghijklmnopqrstuvwx"}):
            manager = ApiKeyManager()
            masked = manager.get_masked_key("OPENROUTER_API_KEY")
            assert masked == "sk-o...uvwx"
            
            # Test key that doesn't exist
            assert manager.get_masked_key("NONEXISTENT_KEY") == ""


def test_get_api_key_manager_singleton():
    """Test that get_api_key_manager returns a singleton instance."""
    manager1 = get_api_key_manager()
    manager2 = get_api_key_manager()
    
    assert manager1 is manager2