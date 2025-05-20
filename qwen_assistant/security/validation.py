"""
Request and response validation module for Qwen Multi-Assistant.

This module provides functionality for validating and sanitizing
input and output data for security purposes.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class RequestValidator:
    """
    Validates and sanitizes incoming requests to the application.

    This class provides:
    - Input validation for user messages
    - Parameter validation for tool calls
    - Content policy enforcement
    """

    # Patterns for potentially malicious content
    MALICIOUS_PATTERNS = [
        r"<script.*?>.*?</script>",
        r"<script.*?>",
        r"</script>",
        r"javascript:.*?\(",
        r"onerror=",
        r"onload=",
        r"eval\(",
        r"document\.cookie",
        r"localStorage",
        r"sessionStorage",
    ]

    def __init__(self, max_message_length: int = 32000):
        """
        Initialize the request validator.

        Args:
            max_message_length: Maximum allowed length for user messages
        """
        self.max_message_length = max_message_length

    def validate_user_message(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a user message for security concerns.

        Args:
            message: User message to validate

        Returns:
            Tuple of (is_valid, error_message or None)
        """
        if not message:
            return False, "Message cannot be empty"

        if len(message) > self.max_message_length:
            return (
                False,
                f"Message exceeds maximum length of {self.max_message_length} characters",
            )

        # Check for potentially malicious content
        for pattern in self.MALICIOUS_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return False, "Message contains potentially harmful content"

        return True, None

    def validate_tool_parameters(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate parameters for a tool call.

        Args:
            tool_name: Name of the tool being called
            parameters: Parameters for the tool call

        Returns:
            Tuple of (is_valid, error_message or None)
        """
        # Tool-specific validation could be added here
        # For now, we'll do some basic checks

        if not tool_name:
            return False, "Tool name cannot be empty"

        if not isinstance(parameters, dict):
            return False, "Parameters must be a dictionary"

        # Convert any parameters to strings and check for malicious content
        for key, value in parameters.items():
            if isinstance(value, str):
                for pattern in self.MALICIOUS_PATTERNS:
                    if re.search(pattern, value, re.IGNORECASE):
                        return (
                            False,
                            f"Parameter '{key}' contains potentially harmful content",
                        )

        return True, None

    def sanitize_input(
        self, data: Union[str, Dict[str, Any]]
    ) -> Union[str, Dict[str, Any]]:
        """
        Sanitize input data to remove potentially harmful content.

        Args:
            data: Input data to sanitize

        Returns:
            Sanitized input data
        """
        if isinstance(data, str):
            # Replace potentially harmful patterns in strings
            sanitized = data
            for pattern in self.MALICIOUS_PATTERNS:
                sanitized = re.sub(pattern, "[REMOVED]", sanitized, flags=re.IGNORECASE)
            return sanitized
        elif isinstance(data, dict):
            # Recursively sanitize dictionary values
            sanitized = {}
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    sanitized[key] = self.sanitize_input(value)
                elif isinstance(value, str):
                    sanitized[key] = self.sanitize_input(value)
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(data, list):
            # Recursively sanitize list items
            return [self.sanitize_input(item) for item in data]
        else:
            # Return non-string, non-container types as is
            return data


class ResponseValidator:
    """
    Validates and sanitizes outgoing responses from the application.

    This class provides:
    - Output validation for system responses
    - Secure handling of error messages
    - Sensitive data filtering
    """

    def __init__(self):
        """Initialize the response validator."""
        pass

    def validate_agent_response(
        self, response: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an agent response for security concerns.

        Args:
            response: Agent response to validate

        Returns:
            Tuple of (is_valid, error_message or None)
        """
        if not isinstance(response, dict):
            return False, "Response must be a dictionary"

        # Ensure response has required fields
        required_fields = ["message"]
        for field in required_fields:
            if field not in response:
                return False, f"Response is missing required field: {field}"

        # Check message content
        if "message" in response and isinstance(response["message"], str):
            message = response["message"]
            if len(message) > 100000:  # Arbitrary limit to prevent excessive responses
                return False, "Response message is too large"

        return True, None

    def sanitize_error_messages(self, error: str) -> str:
        """
        Sanitize error messages to avoid leaking sensitive information.

        Args:
            error: Error message to sanitize

        Returns:
            Sanitized error message
        """
        # Common patterns that might contain sensitive info in errors
        sensitive_patterns = [
            r"(password|secret|key|token)=\'[^\']+\'",
            r'(password|secret|key|token)="[^"]+"',
            r"(password|secret|key|token)=[^\s,)]+",
            r"ConnectionString=[^\s]*",
        ]

        sanitized = error
        for pattern in sensitive_patterns:
            if "ConnectionString" in pattern:
                sanitized = re.sub(
                    pattern,
                    "ConnectionString=[REDACTED]",
                    sanitized,
                    flags=re.IGNORECASE,
                )
            else:
                sanitized = re.sub(
                    pattern,
                    r"\1=[REDACTED]",
                    sanitized,
                    flags=re.IGNORECASE,
                )

        return sanitized

    def prepare_safe_response(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Prepare a safe response object for the client.

        Args:
            success: Whether the operation was successful
            data: Optional data to include in the response
            error: Optional error message

        Returns:
            Safe response dictionary
        """
        response = {"success": success}

        if data is not None:
            # Remove any internal fields that shouldn't be exposed
            safe_data = self._remove_internal_fields(data)
            response["data"] = safe_data

        if error is not None:
            response["error"] = self.sanitize_error_messages(error)

        return response

    def _remove_internal_fields(self, data: Any) -> Any:
        """
        Remove internal fields that shouldn't be exposed to clients.

        Args:
            data: Data to process

        Returns:
            Data with internal fields removed
        """
        if isinstance(data, dict):
            # Create a new dict without internal fields
            result = {}
            for key, value in data.items():
                # Skip keys that start with _ or internal
                if key.startswith("_") or key == "internal":
                    continue

                # Recursively process nested structures
                result[key] = self._remove_internal_fields(value)
            return result
        elif isinstance(data, list):
            # Process each item in the list
            return [self._remove_internal_fields(item) for item in data]
        else:
            # Return primitive values as is
            return data


# Singleton instances
_request_validator = None
_response_validator = None


def get_request_validator() -> RequestValidator:
    """
    Get the singleton RequestValidator instance.

    Returns:
        The shared RequestValidator instance
    """
    global _request_validator
    if _request_validator is None:
        _request_validator = RequestValidator()
    return _request_validator


def get_response_validator() -> ResponseValidator:
    """
    Get the singleton ResponseValidator instance.

    Returns:
        The shared ResponseValidator instance
    """
    global _response_validator
    if _response_validator is None:
        _response_validator = ResponseValidator()
    return _response_validator
