"""
Central security manager for Qwen Multi-Assistant.

This module provides a unified interface to all security functionality
in the application.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union, Tuple

from .api_keys import get_api_key_manager, ApiKeyManager
from .auth import get_auth, Auth, require_auth
from .data_protection import get_data_protection, DataProtection
from .validation import get_request_validator, get_response_validator
from .logging import get_security_logger, SecurityLogger

logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Central manager for all security functionality in the application.
    
    This class provides a unified interface to:
    - API key management
    - Authentication
    - Data protection
    - Request/response validation
    - Security logging
    
    It serves as the main entry point for all security-related operations.
    """
    
    def __init__(self, 
                config: Optional[Dict[str, Any]] = None,
                log_dir: Optional[str] = None):
        """
        Initialize the security manager.
        
        Args:
            config: Optional configuration dictionary
            log_dir: Optional directory for security logs
        """
        self.config = config or {}
        
        # Initialize all security components
        self.api_key_manager = get_api_key_manager()
        self.auth = get_auth()
        self.data_protection = get_data_protection()
        self.request_validator = get_request_validator()
        self.response_validator = get_response_validator()
        self.security_logger = get_security_logger(log_dir)
        
        logger.info("Security manager initialized")
    
    def validate_api_keys(self) -> Dict[str, Dict]:
        """
        Validate all API keys.
        
        Returns:
            Dictionary with validation results for each key
        """
        results = self.api_key_manager.validate_keys()
        
        # Log validation results
        for key_name, result in results.items():
            if result["required"] and not result["present"]:
                self.security_logger.log_event(
                    event_type="configuration_change",
                    message=f"Required API key missing: {key_name}",
                    severity="ERROR"
                )
            elif result["present"] and not result["valid"]:
                self.security_logger.log_event(
                    event_type="configuration_change",
                    message=f"API key has invalid format: {key_name}",
                    severity="WARNING"
                )
                
        return results
    
    def get_api_key(self, key_name: str) -> Optional[str]:
        """
        Get an API key by name.
        
        Args:
            key_name: Name of the API key to retrieve
            
        Returns:
            The API key value or None if not found
        """
        key = self.api_key_manager.get_key(key_name)
        
        # Log access to API key (masked)
        if key:
            masked_key = self.api_key_manager.get_masked_key(key_name)
            self.security_logger.log_access_event(
                resource=f"api_key:{key_name}",
                action="read",
                success=True,
                details={"masked_key": masked_key}
            )
        else:
            self.security_logger.log_access_event(
                resource=f"api_key:{key_name}",
                action="read",
                success=False,
                details={"error": "Key not found"}
            )
            
        return key
    
    def create_session(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Create a new authentication session.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            Session data including tokens and expiration
        """
        session = self.auth.create_session(user_id)
        
        # Log session creation
        self.security_logger.log_auth_event(
            message="Session created",
            user_id=user_id,
            success=True,
            details={"session_id": session["session_id"]}
        )
        
        return session
    
    def validate_session(self, access_token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate an access token and return the associated session.
        
        Args:
            access_token: The access token to validate
            
        Returns:
            Tuple of (is_valid, session_data or None)
        """
        is_valid, session = self.auth.validate_token(access_token)
        
        # Log validation result
        if is_valid and session:
            self.security_logger.log_auth_event(
                message="Session validated",
                user_id=session.get("user_id"),
                success=True,
                details={"session_id": session.get("session_id")}
            )
        else:
            self.security_logger.log_auth_event(
                message="Invalid session token",
                success=False
            )
            
        return is_valid, session
    
    def end_session(self, session_id: str) -> bool:
        """
        End an authentication session.
        
        Args:
            session_id: The ID of the session to end
            
        Returns:
            True if session was found and ended, False otherwise
        """
        result = self.auth.invalidate_session(session_id)
        
        # Log session end
        self.security_logger.log_auth_event(
            message="Session ended",
            success=result,
            details={"session_id": session_id}
        )
        
        return result
    
    def validate_user_message(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a user message for security concerns.
        
        Args:
            message: User message to validate
            
        Returns:
            Tuple of (is_valid, error_message or None)
        """
        is_valid, error = self.request_validator.validate_user_message(message)
        
        # Log validation result if invalid
        if not is_valid:
            self.security_logger.log_security_violation(
                violation_type="input_validation",
                message=f"Invalid user message: {error}",
                details={"message_length": len(message)}
            )
            
        return is_valid, error
    
    def validate_tool_call(self, 
                          tool_name: str, 
                          parameters: Dict[str, Any],
                          user_id: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate a tool call for security concerns.
        
        Args:
            tool_name: Name of the tool being called
            parameters: Parameters for the tool call
            user_id: Optional ID of the user making the call
            
        Returns:
            Tuple of (is_valid, error_message or None)
        """
        is_valid, error = self.request_validator.validate_tool_parameters(tool_name, parameters)
        
        # Log tool call and validation result
        success = is_valid
        details = {
            "tool_name": tool_name,
            "parameters": self.data_protection.clean_request_data(parameters)
        }
        
        if not is_valid:
            details["error"] = error
            self.security_logger.log_security_violation(
                violation_type="tool_validation",
                message=f"Invalid tool call: {error}",
                user_id=user_id,
                details=details
            )
        else:
            self.security_logger.log_tool_usage(
                tool_name=tool_name,
                action="call",
                user_id=user_id,
                success=True,
                details=details
            )
            
        return is_valid, error
    
    def sanitize_response(self, 
                         response: Dict[str, Any],
                         user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Sanitize a response to remove sensitive information.
        
        Args:
            response: Response to sanitize
            user_id: Optional ID of the user receiving the response
            
        Returns:
            Sanitized response
        """
        # Validate response structure
        is_valid, error = self.response_validator.validate_agent_response(response)
        
        if not is_valid:
            # Log validation error
            self.security_logger.log_security_violation(
                violation_type="response_validation",
                message=f"Invalid response format: {error}",
                user_id=user_id
            )
            
            # Return safe error response
            return self.response_validator.prepare_safe_response(
                success=False,
                error="Internal response format error"
            )
        
        # Prepare safe response
        return self.response_validator.prepare_safe_response(
            success=True,
            data=response
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
        if details:
            # Clean sensitive data from details
            details = self.data_protection.clean_request_data(details)
            
        self.security_logger.log_api_request(
            endpoint=endpoint,
            method=method,
            user_id=user_id,
            status_code=status_code,
            details=details
        )


# Singleton instance
_security_manager = None

def get_security_manager(
    config: Optional[Dict[str, Any]] = None,
    log_dir: Optional[str] = None
) -> SecurityManager:
    """
    Get the singleton SecurityManager instance.
    
    Args:
        config: Optional configuration dictionary
        log_dir: Optional directory for security logs
        
    Returns:
        The shared SecurityManager instance
    """
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager(config, log_dir)
    return _security_manager