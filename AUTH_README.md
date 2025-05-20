# Authentication Layer for Qwen Multi-Assistant

This module provides a secure authentication management system for handling API keys and credentials for the Qwen Multi-Assistant project.

## Features

- **Multiple Storage Options**: Support for both `.env` file and system keyring
- **Credential Validation**: Check for required credentials with clear reporting
- **Scope-Based Management**: Group credentials by their usage scope
- **Secure Access**: Centralized access to credentials with proper encapsulation

## Credential Storage Options

### Environment Variables (Default)

By default, credentials are stored in a `.env` file using python-dotenv. This approach is:
- Simple to set up
- Compatible with most deployment environments
- Easy to understand and debug

### System Keyring (More Secure)

For enhanced security, credentials can be stored in the system's secure credential store using the keyring library. This approach:
- Leverages OS-level security mechanisms
- Protects sensitive credentials from accidental exposure
- Works across different platforms (Windows, macOS, Linux)

## Required Credentials

The authentication manager maintains metadata about each credential, including:
- **Description**: Human-readable explanation of the credential's purpose
- **Scope**: Which component uses this credential (LLM, AIRTABLE, EXA, etc.)
- **Required**: Whether the credential is mandatory for system operation

Key credentials include:
- `OPENROUTER_API_KEY`: Required for accessing Qwen3 models
- `AIRTABLE_API_KEY`: Required for the Data Agent
- `EXA_API_KEY`: Required for the Search Agent
- `CONTEXT7_TOKEN`: Optional for the Documentation Agent
- `DESKTOP_COMMANDER_TOKEN`: Optional for the Desktop Agent

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

3. Use the authentication manager in your code:
   ```python
   from src.auth import AuthManager, AuthScope

   # Initialize with default config (uses .env file)
   auth_manager = AuthManager()

   # Check if all required credentials are available
   valid, missing = auth_manager.validate_credentials()
   if not valid:
       print(f"Missing credentials: {missing}")

   # Get a specific credential
   api_key = auth_manager.get_credential("OPENROUTER_API_KEY")

   # Get all credentials for a scope
   airtable_creds = auth_manager.get_credentials_for_scope(AuthScope.AIRTABLE)
   ```

4. Run the example script:
   ```bash
   python example.py
   ```

## Using System Keyring

To use the system keyring instead of a `.env` file:

```python
from src.auth import AuthManager
from pydantic import BaseModel

# Define custom auth config
class CustomAuthConfig(BaseModel):
    use_keyring: bool = True
    service_name: str = "my_service_name"

# Initialize auth manager with custom config
auth_config = CustomAuthConfig()
auth_manager = AuthManager(config=auth_config)

# Now credentials will be stored and retrieved from system keyring
auth_manager.set_credential("MY_API_KEY", "secret-value")
```

## Implementation Details

The authentication system consists of:

1. **CredentialStore**: Abstract base class defining the interface for credential storage
   - `DotenvCredentialStore`: Stores credentials in a `.env` file
   - `KeyringCredentialStore`: Stores credentials in the system keyring
   - `MemoryCredentialStore`: In-memory storage for testing

2. **AuthManager**: Central manager for handling credentials
   - Manages credential metadata
   - Validates required credentials
   - Provides access to credentials by key or scope

3. **AuthScope**: Enum defining different credential scopes
   - LLM: For LLM API access
   - AIRTABLE: For Airtable MCP
   - EXA: For Exa MCP
   - DESKTOP: For DesktopCommander MCP
   - CONTEXT7: For Context7 MCP
