"""Authentication manager for Qwen Multi-Assistant."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union

from loguru import logger
from pydantic import BaseModel, Field

from .credential_store import CredentialStore, DotenvCredentialStore


class AuthScope(str, Enum):
    """Authentication scopes for different MCP servers and services."""
    
    LLM = "llm"  # For LLM API (OpenRouter)
    AIRTABLE = "airtable"  # For Airtable MCP
    EXA = "exa"  # For Exa MCP
    DESKTOP = "desktop"  # For DesktopCommander MCP
    CONTEXT7 = "context7"  # For Context7 MCP


@dataclass
class CredentialInfo:
    """Information about a credential."""
    
    key: str
    description: str
    scope: AuthScope
    required: bool = True
    validation_fn: Optional[callable] = None


class AuthConfig(BaseModel):
    """Configuration model for authentication settings."""
    
    credentials_file: str = Field(
        default=".env",
        description="Path to the credentials file (.env)",
    )
    use_keyring: bool = Field(
        default=False,
        description="Whether to use system keyring for credential storage",
    )
    service_name: str = Field(
        default="qwen_assistant",
        description="Service name for keyring storage",
    )


class AuthManager:
    """Manager for authentication credentials and secure storage."""

    # Define all known credential keys and their metadata
    CREDENTIAL_DEFINITIONS: Dict[str, CredentialInfo] = {
        # LLM API credentials
        "OPENROUTER_API_KEY": CredentialInfo(
            key="OPENROUTER_API_KEY",
            description="OpenRouter API key for accessing Qwen3 models",
            scope=AuthScope.LLM,
            required=True,
        ),
        # Airtable MCP credentials
        "AIRTABLE_API_KEY": CredentialInfo(
            key="AIRTABLE_API_KEY",
            description="Airtable API key for data agent",
            scope=AuthScope.AIRTABLE,
            required=True,
        ),
        # Exa MCP credentials
        "EXA_API_KEY": CredentialInfo(
            key="EXA_API_KEY",
            description="Exa API key for search agent",
            scope=AuthScope.EXA,
            required=True,
        ),
        # Context7 credentials
        "CONTEXT7_TOKEN": CredentialInfo(
            key="CONTEXT7_TOKEN",
            description="Context7 token for documentation agent",
            scope=AuthScope.CONTEXT7,
            required=False,
        ),
        # DesktopCommander credentials (if needed)
        "DESKTOP_COMMANDER_TOKEN": CredentialInfo(
            key="DESKTOP_COMMANDER_TOKEN",
            description="DesktopCommander token (if needed)",
            scope=AuthScope.DESKTOP,
            required=False,
        ),
    }

    def __init__(self, config: Optional[Union[AuthConfig, dict]] = None):
        """Initialize the authentication manager.
        
        Args:
            config: Authentication configuration
        """
        # Set up default config
        if isinstance(config, dict):
            self.config = AuthConfig(**config)
        elif config is None:
            self.config = AuthConfig()
        else:
            self.config = config
        
        # Set up credential store
        if self.config.use_keyring:
            # Import here to avoid circular imports
            from .credential_store import KeyringCredentialStore
            self.credential_store = KeyringCredentialStore(
                service_name=self.config.service_name
            )
        else:
            self.credential_store = DotenvCredentialStore(
                env_file=self.config.credentials_file
            )
    
    def get_credential(self, key: str) -> Optional[str]:
        """Get a credential by key.
        
        Args:
            key: Credential key to retrieve
            
        Returns:
            The credential value or None if not found
        """
        return self.credential_store.get_credential(key)
    
    def set_credential(self, key: str, value: str) -> None:
        """Set a credential value.
        
        Args:
            key: Credential key
            value: Credential value to store
        """
        self.credential_store.set_credential(key, value)
    
    def delete_credential(self, key: str) -> None:
        """Delete a credential.
        
        Args:
            key: Credential key to delete
        """
        self.credential_store.delete_credential(key)
    
    def get_credentials_for_scope(self, scope: AuthScope) -> Dict[str, str]:
        """Get all credentials for a specific scope.
        
        Args:
            scope: Authentication scope to retrieve credentials for
            
        Returns:
            Dictionary of credential keys and values for the scope
        """
        result = {}
        for cred_key, cred_info in self.CREDENTIAL_DEFINITIONS.items():
            if cred_info.scope == scope:
                value = self.get_credential(cred_key)
                if value:
                    result[cred_key] = value
        return result

    
    def validate_credentials(self, scope: Optional[AuthScope] = None) -> Tuple[bool, List[str]]:
        """Validate required credentials are available.
        
        Args:
            scope: Optional scope to validate credentials for.
                  If None, validate all credentials.
            
        Returns:
            Tuple of (is_valid, missing_credentials)
        """
        missing = []
        
        for cred_key, cred_info in self.CREDENTIAL_DEFINITIONS.items():
            # Skip if scope doesn't match
            if scope is not None and cred_info.scope != scope:
                continue
                
            # Check required credentials
            if cred_info.required:
                value = self.get_credential(cred_key)
                if not value:
                    missing.append(cred_key)
                    logger.warning(f"Missing required credential: {cred_key}")
        
        return len(missing) == 0, missing
    
    def get_missing_credentials(self) -> Dict[AuthScope, List[str]]:
        """Get missing required credentials grouped by scope.
        
        Returns:
            Dictionary mapping scopes to lists of missing credential keys
        """
        result: Dict[AuthScope, List[str]] = {}
        
        for cred_key, cred_info in self.CREDENTIAL_DEFINITIONS.items():
            if cred_info.required:
                value = self.get_credential(cred_key)
                if not value:
                    scope = cred_info.scope
                    if scope not in result:
                        result[scope] = []
                    result[scope].append(cred_key)
        
        return result
    
    def get_credential_info(self) -> Dict[str, Dict]:
        """Get information about all credentials.
        
        Returns:
            Dictionary mapping credential keys to metadata
        """
        result = {}
        
        for cred_key, cred_info in self.CREDENTIAL_DEFINITIONS.items():
            value = self.get_credential(cred_key)
            result[cred_key] = {
                "description": cred_info.description,
                "scope": cred_info.scope,
                "required": cred_info.required,
                "is_set": value is not None,
            }
            
        return result
