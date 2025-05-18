"""Logging utilities for Qwen-Assist-2."""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional
import sys

def setup_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """Configure logging based on the provided configuration.
    
    Args:
        config: Logging configuration dictionary. If None, uses default settings.
    """
    if config is None:
        config = {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "logs/app.log"
        }
    
    # Create logs directory if it doesn't exist
    log_file = config.get("file", "logs/app.log")
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set up root logger
    level_name = config.get("level", "INFO")
    level = getattr(logging, level_name.upper())
    log_format = config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(file_handler)
    
    # Suppress overly verbose logs from libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)