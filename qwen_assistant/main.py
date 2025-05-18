"""Main entry point for Qwen-Assist-2."""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qwen_assistant.utils.config import load_config
from qwen_assistant.utils.logging import setup_logging
from qwen_assistant.agents.router import RouterAgent
from qwen_assistant.agents.base import BaseAgent
from qwen_assistant.agents.data import DataAgent
from qwen_assistant.ui.gradio_interface import GradioInterface

logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments.
    
    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Qwen-Assist-2: Multi-agent system")
    parser.add_argument(
        "--config", 
        type=str, 
        default=None,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode"
    )
    return parser.parse_args()

def main():
    """Main entry point."""
    # Parse command line arguments
    args = parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Load configuration
    config = load_config(args.config)
    
    # Set up logging
    log_config = config.get("logging", {})
    if args.debug:
        log_config["level"] = "DEBUG"
    setup_logging(log_config)
    
    logger.info("Starting Qwen-Assist-2")
    
    try:
        # Initialize router agent
        router_agent = RouterAgent(
            llm_config=config.get("llm", {}),
            mcp_config=config.get("mcp_servers", {})
        )
        
        # Initialize data agent
        data_agent = DataAgent(
            llm_config=config.get("llm", {}),
            mcp_config=config.get("mcp_servers", {})
        )
        
        # Set up agent map
        agent_map = {
            "router": router_agent,
            "data": data_agent
        }
        
        # Initialize UI
        ui_config = config.get("ui", {})
        ui = GradioInterface(
            primary_agent=router_agent,
            agent_map=agent_map,
            config=ui_config
        )
        
        # Launch UI
        logger.info(f"Launching UI on port {ui_config.get('port', 7860)}")
        ui.launch()
        
    except Exception as e:
        logger.exception(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()