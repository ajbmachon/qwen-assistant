#!/usr/bin/env python
"""Example usage of the security system."""

from qwen_assistant.security.security_manager import (
    get_security_manager,
    require_auth,
)

def main() -> None:
    """Demonstrate the security system."""

    security = get_security_manager()

    # Validate API keys
    results = security.validate_api_keys()
    print("Qwen Multi-Assistant API Key Status:")
    for key, info in results.items():
        status = "✅" if info["present"] and info["valid"] else "❌"
        if info["required"] and not info["present"]:
            status += " (Required)"
        print(f"  {key}: {status}")

    # Create a session for the demo user
    session = security.create_session("demo_user")
    token = session["access_token"]
    print("\nSession token:", token)

    # Validate the session token
    valid, _ = security.validate_session(token)
    print("Token valid:", valid)

    # Demonstrate the require_auth decorator
    @require_auth
    def protected_action(token=None):
        print("Protected action executed")

    protected_action(token=token)

    print("\nSecurity system demo complete")

if __name__ == "__main__":
    main()
