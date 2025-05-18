"""Configuration utilities for Qwen-Assist-2."""

import os
import yaml
from typing import Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from a YAML file.
    
    Args:
        config_path: Path to the config file. If None, uses default config.
        
    Returns:
        Dict containing the configuration.
    """
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "default_config.yaml"
        )
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Process environment variables
    config = _process_env_vars(config)
    
    return config

def _process_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Process environment variables in the config.
    
    Args:
        config: Configuration dictionary.
        
    Returns:
        Processed configuration dictionary.
    """
    if isinstance(config, dict):
        for key, value in config.items():
            if isinstance(value, dict):
                config[key] = _process_env_vars(value)
            elif isinstance(value, list):
                config[key] = [_process_env_vars(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                if env_var in os.environ:
                    config[key] = os.environ[env_var]
                else:
                    logger.warning(f"Environment variable {env_var} not found.")
                    config[key] = ""
    return config

def get_project_root() -> Path:
    """Return the project root directory as a Path object."""
    return Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))