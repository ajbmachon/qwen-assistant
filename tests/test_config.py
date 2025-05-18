"""Tests for configuration utilities."""

import os
import pytest
from unittest.mock import patch
from src.utils.config import load_config, _process_env_vars

def test_process_env_vars():
    """Test processing of environment variables in config."""
    # Setup test config with env vars
    test_config = {
        "api_key": "${TEST_API_KEY}",
        "nested": {
            "value": "${TEST_NESTED_VALUE}",
            "list": ["item1", "${TEST_LIST_VALUE}"]
        }
    }
    
    # Mock environment variables
    with patch.dict(os.environ, {
        "TEST_API_KEY": "test_key_value",
        "TEST_NESTED_VALUE": "nested_value",
        "TEST_LIST_VALUE": "list_value"
    }):
        processed = _process_env_vars(test_config)
    
    # Verify results
    assert processed["api_key"] == "test_key_value"
    assert processed["nested"]["value"] == "nested_value"
    assert processed["nested"]["list"][1] == "list_value"

def test_process_env_vars_missing():
    """Test handling of missing environment variables."""
    test_config = {"api_key": "${MISSING_ENV_VAR}"}
    
    # Process with missing env var
    with patch.dict(os.environ, {}, clear=True):
        processed = _process_env_vars(test_config)
    
    # Verify results
    assert processed["api_key"] == ""

def test_load_config_file_not_found():
    """Test handling of missing config file."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent_config.yaml")