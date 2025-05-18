"""
Security logging module for Qwen Multi-Assistant.

This module provides enhanced logging functionality for security-related events
and audit trail maintenance.
"""

import logging
import time
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, Union
import uuid

from .data_protection import get_data_protection

logger = logging.getLogger(__name__)

class SecurityLogger:
    """
    Enhanced logger for security events with secure handling of sensitive data.
    
    This class provides:
    - Secure logging of security-related events
    - Audit trail for user actions and system events
    - PII redaction before logging
    """
    
    EVENT_TYPES = {
        "authentication": "AUTH",
        "authorization": "AUTHZ",
        "data_access": "DATA",
        "api_request": "API",
        "tool_usage": "TOOL",
        "security_violation": "SECVIO",
        "configuration_change": "CONFIG",
    }
    
    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialize the security logger.
        
        Args:
            log_dir: Directory to store security logs (if None, use default logger)
        """
        self.log_dir = log_dir
        self.data_protection = get_data_protection()
        
        # Create a separate file handler for security events if log_dir is specified
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Set up the security logger with appropriate handlers."""
        self.security_logger = logging.getLogger("qwen_assistant.security")
        
        # Set level to INFO to ensure all security events are logged
        self.security_logger.setLevel(logging.INFO)
        
        # Add file handler if log_dir is specified
        if self.log_dir:
            log_file = os.path.join(self.log_dir, f"security_{datetime.now().strftime('%Y%m%d')}.log")
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            self.security_logger.addHandler(handler)
    
    def log_event(self, 
                 event_type: str, 
                 message: str, 
                 details: Optional[Dict[str, Any]] = None,
                 user_id: Optional[str] = None,
                 severity: str = "INFO") -> None:
        """
        Log a security event with standardized format.
        
        Args:
            event_type: Type of security event (see EVENT_TYPES)
            message: Brief description of the event
            details: Additional details about the event
            user_id: ID of the user related to the event
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
        """
        event_code = self.EVENT_TYPES.get(event_type, "GENERAL")
        
        # Create event ID for correlation
        event_id = str(uuid.uuid4())
        
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_id": event_id,
            "event_type": event_type,
            "event_code": event_code,
            "message": message,
            "user_id": user_id,
        }
        
        # Add details if provided, with sensitive data redacted
        if details:
            sanitized_details = self.data_protection.sanitize_logs(details)
            log_entry["details"] = sanitized_details
        
        # Determine log level and log the event
        log_level = getattr(logging, severity.upper())
        log_message = json.dumps(log_entry)
        
        self.security_logger.log(log_level, log_message)
    
    def log_auth_event(self, 
                      message: str, 
                      user_id: Optional[str] = None,
                      success: bool = True,
                      details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an authentication event.
        
        Args:
            message: Description of the auth event
            user_id: ID of the user being authenticated
            success: Whether authentication was successful
            details: Additional details about the event
        """
        severity = "INFO" if success else "WARNING"
        
        self.log_event(
            event_type="authentication",
            message=message,
            details=details,
            user_id=user_id,
            severity=severity
        )
    
    def log_access_event(self,
                        resource: str,
                        action: str,
                        user_id: Optional[str] = None,
                        success: bool = True,
                        details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a resource access event.
        
        Args:
            resource: Resource being accessed
            action: Action performed on the resource
            user_id: ID of the user accessing the resource
            success: Whether access was granted
            details: Additional details about the event
        """
        message = f"Resource access: {action} on {resource}"
        severity = "INFO" if success else "WARNING"
        
        self.log_event(
            event_type="authorization",
            message=message,
            details=details,
            user_id=user_id,
            severity=severity
        )
    
    def log_api_request(self,
                       endpoint: str,
                       method: str,
                       user_id: Optional[str] = None,
                       status_code: Optional[int] = None,
                       details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an API request.
        
        Args:
            endpoint: API endpoint being accessed
            method: HTTP method used
            user_id: ID of the user making the request
            status_code: HTTP status code of the response
            details: Additional details about the request
        """
        message = f"{method} {endpoint}"
        if status_code:
            message += f" (Status: {status_code})"
            
        # Determine severity based on status code
        severity = "INFO"
        if status_code:
            if status_code >= 400 and status_code < 500:
                severity = "WARNING"
            elif status_code >= 500:
                severity = "ERROR"
        
        self.log_event(
            event_type="api_request",
            message=message,
            details=details,
            user_id=user_id,
            severity=severity
        )
    
    def log_security_violation(self,
                              violation_type: str,
                              message: str,
                              user_id: Optional[str] = None,
                              details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a security violation.
        
        Args:
            violation_type: Type of security violation
            message: Description of the violation
            user_id: ID of the user related to the violation
            details: Additional details about the violation
        """
        self.log_event(
            event_type="security_violation",
            message=f"{violation_type}: {message}",
            details=details,
            user_id=user_id,
            severity="WARNING"
        )
    
    def log_tool_usage(self,
                      tool_name: str,
                      action: str,
                      user_id: Optional[str] = None,
                      success: bool = True,
                      details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log tool usage by an agent.
        
        Args:
            tool_name: Name of the tool being used
            action: Action performed with the tool
            user_id: ID of the user whose session is using the tool
            success: Whether the tool usage was successful
            details: Additional details about the tool usage
        """
        message = f"Tool usage: {tool_name} {action}"
        severity = "INFO" if success else "WARNING"
        
        self.log_event(
            event_type="tool_usage",
            message=message,
            details=details,
            user_id=user_id,
            severity=severity
        )


# Singleton instance
_security_logger = None

def get_security_logger(log_dir: Optional[str] = None) -> SecurityLogger:
    """
    Get the singleton SecurityLogger instance.
    
    Args:
        log_dir: Optional directory for security logs
        
    Returns:
        The shared SecurityLogger instance
    """
    global _security_logger
    if _security_logger is None:
        _security_logger = SecurityLogger(log_dir)
    return _security_logger