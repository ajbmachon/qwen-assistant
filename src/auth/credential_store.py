"""Credential storage for Qwen Multi-Assistant."""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

import keyring
from dotenv import load_dotenv
from loguru import logger


class CredentialStore(ABC):
    """Abstract base class for credential storage strategies."""

    @abstractmethod
    def get_credential(self, key: str) -> Optional[str]:
        """Get a credential value by key.
        
        Args:
            key: The credential key to retrieve
            
        Returns:
            The credential value or None if not found
        """
        pass

    @abstractmethod
    def set_credential(self, key: str, value: str) -> None:
        """Store a credential value.
        
        Args:
            key: The credential key
            value: The credential value to store
        """
        pass

    @abstractmethod
    def delete_credential(self, key: str) -> None:
        """Delete a credential.
        
        Args:
            key: The credential key to delete
        """
        pass

    @abstractmethod
    def list_credentials(self) -> List[str]:
        """List all available credential keys.
        
        Returns:
            A list of credential keys
        """
        pass


class DotenvCredentialStore(CredentialStore):
    """Credential storage using .env file."""

    def __init__(self, env_file: Union[str, Path] = ".env"):
        """Initialize the dotenv credential store.
        
        Args:
            env_file: Path to the .env file
        """
        self.env_file = Path(env_file)
        # Load environment variables from .env file
        load_dotenv(dotenv_path=self.env_file)
    
    def get_credential(self, key: str) -> Optional[str]:
        """Get a credential from environment variables.
        
        Args:
            key: The credential key
            
        Returns:
            The credential value or None if not found
        """
        return os.environ.get(key)
    
    def set_credential(self, key: str, value: str) -> None:
        """Set a credential in the .env file.
        
        Note: This method updates the .env file directly, which may
        override formatting or comments in the file.
        
        Args:
            key: The credential key
            value: The credential value to store
        """
        # Read current .env file
        env_vars = {}
        if self.env_file.exists():
            with open(self.env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        env_vars[k] = v
        
        # Update or add the new value
        env_vars[key] = value
        
        # Write back to .env file
        with open(self.env_file, "w") as f:
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")
        
        # Also update current environment
        os.environ[key] = value
    
    def delete_credential(self, key: str) -> None:
        """Delete a credential from the .env file.
        
        Args:
            key: The credential key to delete
        """
        # Read current .env file
        env_vars = {}
        if self.env_file.exists():
            with open(self.env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k != key:  # Skip the key to be deleted
                            env_vars[k] = v
        
        # Write back to .env file
        with open(self.env_file, "w") as f:
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")
        
        # Also remove from current environment
        if key in os.environ:
            os.environ.pop(key)
    
    def list_credentials(self) -> List[str]:
        """List all available credential keys in the .env file.
        
        Returns:
            A list of credential keys
        """
        keys = []
        if self.env_file.exists():
            with open(self.env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, _ = line.split("=", 1)
                        keys.append(k)
        return keys


class KeyringCredentialStore(CredentialStore):
    """Credential storage using the system keyring service."""

    def __init__(self, service_name: str = "qwen_assistant"):
        """Initialize the keyring credential store.
        
        Args:
            service_name: Name of the service in the keyring
        """
        self.service_name = service_name
        self._credential_keys: Set[str] = set()
    
    def get_credential(self, key: str) -> Optional[str]:
        """Get a credential from the keyring.
        
        Args:
            key: The credential key
            
        Returns:
            The credential value or None if not found
        """
        try:
            return keyring.get_password(self.service_name, key)
        except Exception as e:
            logger.error(f"Failed to retrieve credential {key} from keyring: {e}")
            return None
    
    def set_credential(self, key: str, value: str) -> None:
        """Store a credential in the keyring.
        
        Args:
            key: The credential key
            value: The credential value to store
        """
        try:
            keyring.set_password(self.service_name, key, value)
            self._credential_keys.add(key)
        except Exception as e:
            logger.error(f"Failed to store credential {key} in keyring: {e}")
    
    def delete_credential(self, key: str) -> None:
        """Delete a credential from the keyring.
        
        Args:
            key: The credential key to delete
        """
        try:
            keyring.delete_password(self.service_name, key)
            if key in self._credential_keys:
                self._credential_keys.remove(key)
        except Exception as e:
            logger.error(f"Failed to delete credential {key} from keyring: {e}")
    
    def list_credentials(self) -> List[str]:
        """List all available credential keys in the keyring.
        
        Note: Keyring doesn't provide a native way to list all entries,
        so this will only return keys that have been added during the
        current session.
        
        Returns:
            A list of credential keys
        """
        return list(self._credential_keys)


class MemoryCredentialStore(CredentialStore):
    """In-memory credential storage for testing purposes."""

    def __init__(self):
        """Initialize an empty in-memory credential store."""
        self._credentials: Dict[str, str] = {}
    
    def get_credential(self, key: str) -> Optional[str]:
        """Get a credential from memory.
        
        Args:
            key: The credential key
            
        Returns:
            The credential value or None if not found
        """
        return self._credentials.get(key)
    
    def set_credential(self, key: str, value: str) -> None:
        """Store a credential in memory.
        
        Args:
            key: The credential key
            value: The credential value to store
        """
        self._credentials[key] = value
    
    def delete_credential(self, key: str) -> None:
        """Delete a credential from memory.
        
        Args:
            key: The credential key to delete
        """
        if key in self._credentials:
            del self._credentials[key]
    
    def list_credentials(self) -> List[str]:
        """List all available credential keys in memory.
        
        Returns:
            A list of credential keys
        """
        return list(self._credentials.keys())
