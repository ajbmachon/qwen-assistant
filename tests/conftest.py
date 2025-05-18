"""Test fixtures for Qwen-Assist-2."""

import os
import sys
import pytest
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Return a test configuration.
    
    Returns:
        Test configuration dictionary.
    """
    return {
        "app": {
            "name": "Qwen-Assist-2-Test",
            "description": "Test configuration for Qwen-Assist-2",
            "version": "0.1.0"
        },
        "llm": {
            "model": "qwen3-32b",
            "model_server": "dashscope",
            "api_key": "test_key"
        },
        "mcp_servers": {
            "context7": {
                "command": "echo",
                "args": ["Mocked Context7 Server"]
            }
        },
        "ui": {
            "port": 7861,
            "share": False,
            "title": "Qwen-Assist-Test",
            "theme": "default"
        },
        "logging": {
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "logs/test.log"
        }
    }