#!/usr/bin/env python
"""Example usage of the authentication system."""

import sys
from pathlib import Path

from src.auth import AuthManager, AuthScope, DotenvCredentialStore, KeyringCredentialStore

def main():
    """Demonstrate the authentication system."""
    # Initialize auth manager with default configuration
    auth_manager = AuthManager()
    
    # Check for missing credentials
    valid, missing = auth_manager.validate_credentials()
    if not valid:
        print(f"⚠️ Missing required credentials: {', '.join(missing)}")
        print("Please set these credentials in your .env file")
    
    # Display credential information
    print("\nQwen Multi-Assistant Authentication Status:")
    for key, info in auth_manager.get_credential_info().items():
        status = "✅ Set" if info["is_set"] else "❌ Missing"
        if info["required"]:
            status += " (Required)"
        print(f"  {key}: {status}")
        print(f"    Description: {info['description']}")
        print(f"    Scope: {info['scope']}")
        print()
    
    # Show credentials by scope
    print("\nCredentials by Scope:")
    for scope in AuthScope:
        creds = auth_manager.get_credentials_for_scope(scope)
        print(f"  {scope.value}: {len(creds)} credential(s) set")
    
    # Demonstrate setting a credential
    print("\nSetting a test credential...")
    auth_manager.set_credential("TEST_CREDENTIAL", "test_value")
    assert auth_manager.get_credential("TEST_CREDENTIAL") == "test_value"
    print("✅ Credential successfully set and retrieved")
    
    # Demonstrate deleting a credential
    print("\nDeleting the test credential...")
    auth_manager.delete_credential("TEST_CREDENTIAL")
    assert auth_manager.get_credential("TEST_CREDENTIAL") is None
    print("✅ Credential successfully deleted")
    
    # Demonstrate using keyring credential store
    print("\nDemonstrating keyring credential store...")
    try:
        keyring_store = KeyringCredentialStore(service_name="qwen_test")
        keyring_store.set_credential("KEYRING_TEST", "test_value")
        value = keyring_store.get_credential("KEYRING_TEST")
        assert value == "test_value"
        keyring_store.delete_credential("KEYRING_TEST")
        print("✅ Keyring credential store works")
    except Exception as e:
        print(f"❌ Keyring credential store failed: {e}")
    
    print("\nAuthentication system demo complete")

if __name__ == "__main__":
    main()
