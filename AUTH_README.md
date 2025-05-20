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

3. Use the security manager in your code:
   ```python
   from qwen_assistant.security.security_manager import get_security_manager

   security = get_security_manager()

   # Validate API keys
   results = security.validate_api_keys()
   for key, info in results.items():
       print(key, info)

   # Create a session and validate it
   session = security.create_session("demo_user")
   valid, _ = security.validate_session(session["access_token"])
   ```

4. Run the example script:
   ```bash
   python example.py
   ```

## Example Script

Run the example script to see the security components in action:

```bash
python example.py
```

## Implementation Details

The authentication system consists of:

1. **ApiKeyManager**: Handles loading and validating API keys from the environment
2. **Auth**: Provides simple session management with token validation
3. **DataProtection**: Redacts sensitive data from logs and requests
4. **Request/Response Validators**: Ensure incoming and outgoing data is safe
5. **SecurityManager**: Convenience wrapper that exposes all of the above

