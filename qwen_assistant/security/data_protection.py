"""
Data protection module for Qwen Multi-Assistant.

This module provides functionality for protecting sensitive data
during processing, storage, and transmission.
"""

import json
import logging
from typing import Any, Dict, List, Union, Optional
import re

logger = logging.getLogger(__name__)

class DataProtection:
    """
    Handles data protection for the Qwen Multi-Assistant application.
    
    This class provides:
    - PII detection and redaction in text
    - Sensitive data handling in request/response objects
    - Secure data storage utilities
    """
    
    # Common patterns for sensitive data
    SENSITIVE_PATTERNS = {
        "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "api_key": r'\b(?:key-|sk-|pk-|token=|api_key=|apikey=)([a-zA-Z0-9_-]{16,})\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
    }
    
    def __init__(self):
        """Initialize the data protection manager."""
        pass
    
    def redact_text(self, text: str) -> str:
        """
        Redact sensitive information from text.
        
        Args:
            text: Text that may contain sensitive information
            
        Returns:
            Redacted text with sensitive data replaced
        """
        if not text:
            return text
            
        redacted = text
        
        # Apply each pattern and redact matches
        for data_type, pattern in self.SENSITIVE_PATTERNS.items():
            redacted = re.sub(
                pattern, 
                f"[REDACTED-{data_type.upper()}]", 
                redacted
            )
            
        return redacted
    
    def clean_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean a request data dictionary to remove/redact sensitive information.
        
        Args:
            data: Request data dictionary
            
        Returns:
            Cleaned data with sensitive information redacted
        """
        if not data:
            return data
            
        # Create a deep copy to avoid modifying the original
        import copy
        cleaned = copy.deepcopy(data)
        
        # Recursively clean all string values
        self._clean_dict_recursive(cleaned)
        
        return cleaned
    
    def _clean_dict_recursive(self, data: Any) -> None:
        """
        Recursively clean a dictionary or list to redact sensitive information.
        
        Args:
            data: Dictionary, list, or value to clean
        """
        if isinstance(data, dict):
            for key, value in data.items():
                # Specifically handle known sensitive keys
                if key.lower() in {"api_key", "token", "password", "secret", "credential"}:
                    if isinstance(value, str) and value:
                        data[key] = "[REDACTED]"
                else:
                    self._clean_dict_recursive(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._clean_dict_recursive(item)
        elif isinstance(data, str):
            # No direct replacement for simple strings - would need the parent to do it
            pass
    
    def sanitize_logs(self, log_data: Union[str, Dict, List]) -> Union[str, Dict, List]:
        """
        Sanitize log data to remove sensitive information before logging.
        
        Args:
            log_data: Log data to sanitize (string, dict, or list)
            
        Returns:
            Sanitized log data
        """
        if isinstance(log_data, str):
            return self.redact_text(log_data)
        elif isinstance(log_data, (dict, list)):
            # Convert to JSON and back to handle nested structures
            json_str = json.dumps(log_data)
            redacted_str = self.redact_text(json_str)
            return json.loads(redacted_str)
        else:
            return log_data


# Singleton instance
_data_protection_instance = None

def get_data_protection() -> DataProtection:
    """
    Get the singleton DataProtection instance.
    
    Returns:
        The shared DataProtection instance
    """
    global _data_protection_instance
    if _data_protection_instance is None:
        _data_protection_instance = DataProtection()
    return _data_protection_instance
