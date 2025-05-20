"""Authentication module for Qwen Multi-Assistant."""

from .auth_manager import AuthManager, AuthScope
from .credential_store import (CredentialStore, DotenvCredentialStore,
                             KeyringCredentialStore, MemoryCredentialStore)

__all__ = [
    "AuthManager", 
    "AuthScope", 
    "CredentialStore", 
    "DotenvCredentialStore",
    "KeyringCredentialStore", 
    "MemoryCredentialStore"
]
