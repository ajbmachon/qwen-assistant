"""
Main entry point for the Qwen Multi-Assistant system.
"""
import argparse
import asyncio
import logging
import os
import sys
from typing import Dict, Any

from .config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main(config_path: str = None):
    """
    Main entry point for the Qwen Multi-Assistant system.
    
    Args:
        config_path: Path to configuration file
    """
    # Load configuration
    config = load_config(config_path)
    logger.info("Configuration loaded")
    
    # Import here to avoid circular imports
    from .agents.desktop import DesktopAgent
    
    # Initialize the Desktop Agent
    desktop_agent_config = config["agents"]["desktop"]
    model_config = config["models"]["agent"]
    
    desktop_agent = DesktopAgent(desktop_agent_config, model_config)
    await desktop_agent.prepare()
    
    logger.info("Desktop Agent initialized")
    
    # For testing, execute a simple command
    response = await desktop_agent.handle_request(
        {"query": "list current directory", "action": "list_directory", "directory": "."},
        {}
    )
    
    print("Desktop Agent Response:")
    print(response)
    
    # Clean up
    await desktop_agent.cleanup()
    
    logger.info("Application terminated")


def run():
    """Run the application from the command line."""
    parser = argparse.ArgumentParser(description="Qwen Multi-Assistant")
    parser.add_argument(
        "--config", 
        help="Path to configuration file",
        default=os.environ.get("QWEN_CONFIG_PATH")
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.config))
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()