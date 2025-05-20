"""
Configuration management for the Qwen Multi-Assistant system.
"""
import os
import yaml
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    # Model configurations
    "models": {
        "router": {
            "model": "qwen3-235b",
            "temperature": 0.4,
            "max_tokens": 1000,
            "top_p": 0.95
        },
        "agent": {
            "model": "qwen3-32b",
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9
        }
    },
    
    # MCP Server configurations
    "mcp_servers": {
        "airtable": {
            "endpoint": "http://localhost:9001",
            "api_key": ""
        },
        "desktop": {
            "endpoint": "http://localhost:9000"
        },
        "exa": {
            "endpoint": "http://localhost:9002",
            "api_key": ""
        },
        "context7": {
            "endpoint": "http://localhost:9003",
            "api_key": ""
        }
    },
    
    # Agent configurations
    "agents": {
        "data": {
            "enabled": True,
            "mcp_endpoint": "http://localhost:9001"
        },
        "desktop": {
            "enabled": True,
            "mcp_endpoint": "http://localhost:9000"
        },
        "search": {
            "enabled": True,
            "mcp_endpoint": "http://localhost:9002"
        },
        "documentation": {
            "enabled": True,
            "mcp_endpoint": "http://localhost:9003"
        }
    },
    
    # UI Configuration
    "ui": {
        "title": "Qwen Multi-Assistant",
        "theme": "default",
        "port": 7860
    }
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file, environment variables, and defaults.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Merged configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    # Load from YAML file if provided
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    _deep_update(config, file_config)
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    # Override with environment variables
    _update_from_env(config)
    
    return config


def _deep_update(target: Dict, source: Dict) -> Dict:
    """
    Update target dictionary with source values, recursively for nested dicts.
    
    Args:
        target: Target dictionary to update
        source: Source dictionary with values to apply
        
    Returns:
        Updated target dictionary
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_update(target[key], value)
        else:
            target[key] = value
    return target


def _update_from_env(config: Dict[str, Any]) -> None:
    """
    Update configuration from environment variables.
    
    Environment variables format:
    - QWEN_MODEL_ROUTER: Router model name
    - QWEN_MCP_DESKTOP_ENDPOINT: Desktop MCP server endpoint
    - QWEN_UI_PORT: Gradio UI port
    - QWEN_UI_TITLE: Title shown in the UI
    
    Args:
        config: Configuration to update
    """
    env_mappings = {
        # Model configurations
        "QWEN_MODEL_ROUTER": ("models", "router", "model"),
        "QWEN_MODEL_AGENT": ("models", "agent", "model"),
        
        # MCP endpoints
        "QWEN_MCP_AIRTABLE_ENDPOINT": ("mcp_servers", "airtable", "endpoint"),
        "QWEN_MCP_DESKTOP_ENDPOINT": ("mcp_servers", "desktop", "endpoint"),
        "QWEN_MCP_EXA_ENDPOINT": ("mcp_servers", "exa", "endpoint"),
        "QWEN_MCP_CONTEXT7_ENDPOINT": ("mcp_servers", "context7", "endpoint"),
        
        # API keys
        "QWEN_API_KEY_AIRTABLE": ("mcp_servers", "airtable", "api_key"),
        "QWEN_API_KEY_EXA": ("mcp_servers", "exa", "api_key"),
        "QWEN_API_KEY_CONTEXT7": ("mcp_servers", "context7", "api_key"),
        
        # UI Configuration
        "QWEN_UI_PORT": ("ui", "port"),
        "QWEN_UI_TITLE": ("ui", "title"),
    }
    
    for env_var, config_path in env_mappings.items():
        value = os.environ.get(env_var)
        if value:
            # Navigate to the correct level in the config
            target = config
            for i, part in enumerate(config_path):
                if i == len(config_path) - 1:
                    # Convert port to int
                    if part == "port":
                        try:
                            target[part] = int(value)
                        except ValueError:
                            logger.error(f"Invalid port value: {value}")
                    else:
                        target[part] = value
                else:
                    target = target[part]

