"""
API key management module for Qwen Multi-Assistant.

This module provides secure loading, storage, and access to API keys
used by the application, including the main LLM API and various MCP servers.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Union
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class ApiKeyManager:
    """
    Manages API keys for the application, ensuring they are securely stored and accessed.
    
    This class handles:
    - Loading API keys from environment variables
    - Validating API key format and presence
    - Providing secure access to keys when needed by agents
    - Obscuring key values in logs and UI
    """
    
    # Define known API keys and their validation patterns
    KEY_DEFINITIONS = {
        "OPENROUTER_API_KEY": {
            "description": "Main LLM API Key (OpenRouter)",
            "required": True,
            "format": r"^sk-or-[a-zA-Z0-9]{24,}$",
        },
        "EXA_API_KEY": {
            "description": "Exa Search MCP Server API Key",
            "required": True,
            "format": r"^exa-[a-zA-Z0-9]{32,}$",
        },
        "AIRTABLE_API_KEY": {
            "description": "Airtable MCP Server API Key",
            "required": True,
            "format": r"^(pat|key)[a-zA-Z0-9]{14,}$",
        },
        "CONTEXT7_TOKEN": {
            "description": "Context7 MCP Server Token",
            "required": False,
            "format": r"^[a-zA-Z0-9_-]{10,}$",
        }
    }
    
    def __init__(self, env_path: Optional[Union[str, Path]] = None):
        """
        Initialize the API key manager.
        
        Args:
            env_path: Optional path to a .env file to load keys from
        """
        self._keys = {}
        self._load_from_env(env_path)
    
    def _load_from_env(self, env_path: Optional[Union[str, Path]] = None) -> None:
        """
        Load API keys from environment variables, optionally from a specified .env file.
        
        Args:
            env_path: Optional path to a .env file
        """
        # Always check current environment first
        for key_name in self.KEY_DEFINITIONS:
            if key_name in os.environ:
                self._keys[key_name] = os.environ[key_name]
    
    def validate_keys(self) -> Dict[str, Dict]:
        """
        Validate all required API keys are present and have valid formats.
        
        Returns:
            Dictionary with validation results for each key
        """
        import re
        
        results = {}
        
        for key_name, definition in self.KEY_DEFINITIONS.items():
            result = {
                "present": key_name in self._keys,
                "valid": False,
                "required": definition["required"],
                "description": definition["description"]
            }
            
            if result["present"]:
                # Validate format if key is present
                result["valid"] = bool(re.match(definition["format"], self._keys[key_name]))
            
            results[key_name] = result
            
            # Log validation issues
            if definition["required"] and not result["present"]:
                logger.error(f"Required API key missing: {key_name} ({definition['description']})")
            elif result["present"] and not result["valid"]:
                logger.error(f"API key has invalid format: {key_name}")
                
        return results
    
    @property
    def missing_required_keys(self) -> bool:
        """
        Check if any required API keys are missing.
        
        Returns:
            True if any required keys are missing, otherwise False
        """
        validation = self.validate_keys()
        return any(info["required"] and not info["present"] for _, info in validation.items())
    
    def get_key(self, key_name: str) -> Optional[str]:
        """
        Get an API key by name.
        
        Args:
            key_name: Name of the API key to retrieve
            
        Returns:
            The API key value or None if not found
        """
        return self._keys.get(key_name)
    
    def mask_key(self, key: str) -> str:
        """
        Mask an API key for display/logging purposes.
        
        Args:
            key: The API key to mask
            
        Returns:
            A masked version of the key that hides most characters
        """
        if not key:
            return ""
        
        # Show first 4 and last 4 characters, mask the rest
        if len(key) <= 8:
            return "*" * len(key)
        
        return f"{key[:4]}...{key[-4:]}"
    
    def get_masked_key(self, key_name: str) -> str:
        """
        Get a masked version of an API key.
        
        Args:
            key_name: Name of the API key to retrieve in masked form
            
        Returns:
            Masked API key or empty string if key not found
        """
        key = self.get_key(key_name)
        if key:
            return self.mask_key(key)
        return ""


@lru_cache(maxsize=1)
def get_api_key_manager(env_path: Optional[str] = None) -> ApiKeyManager:
    """
    Get a singleton instance of the API key manager.
    
    Args:
        env_path: Optional path to a .env file
        
    Returns:
        Singleton ApiKeyManager instance
    """
    return ApiKeyManager(env_path)