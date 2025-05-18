"""
Main module for the Qwen-Assist-2 system.

This module provides the entry point for the application.
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv

from qwen_assistant.agents.router import RouterAgent
from qwen_agent.gui import WebUI
from qwen_agent.utils.output_beautify import typewriter_print

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("qwen_assistant.log"),
    ],
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        The loaded configuration as a dictionary.
    """
    if not os.path.exists(config_path):
        logger.error(f"Config file not found at: {config_path}")
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        raise


def process_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process environment variables in the configuration.
    
    Replaces values with pattern ${ENV_VAR} with the actual environment variable.
    
    Args:
        config: The configuration dictionary.
        
    Returns:
        The processed configuration.
    """
    if isinstance(config, dict):
        for key, value in config.items():
            if isinstance(value, dict):
                config[key] = process_env_vars(value)
            elif isinstance(value, list):
                config[key] = [process_env_vars(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                if env_var in os.environ:
                    config[key] = os.environ[env_var]
                    logger.debug(f"Replaced environment variable: {key}")
                else:
                    logger.warning(f"Environment variable {env_var} not found")
                    config[key] = ""
    return config


def main(config_path: Optional[str] = None, use_gui: bool = False) -> None:
    """
    Main entry point for the Qwen-Assist-2 system.
    
    Args:
        config_path: Path to the configuration file. If None, uses default config.
        use_gui: Whether to launch the Gradio UI.
    """
    # Load environment variables
    load_dotenv()
    
    # Load configuration
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config",
            "config.yaml"
        )
        if not os.path.exists(config_path):
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config",
                "default_config.yaml"
            )
    
    try:
        # Load and process configuration
        config = load_config(config_path)
        config = process_env_vars(config)
        
        # Create the Router Agent
        router = RouterAgent(
            name=config.get("app", {}).get("name", "Qwen-Assist-2"),
            description=config.get("app", {}).get("description", "Multi-agent system built on the Qwen3 LLM"),
            llm_config=config.get("llm", {}),
            mcp_config=config.get("mcp_servers", {}),
        )
        
        if use_gui:
            # Launch the Gradio UI
            logger.info("Launching Gradio UI...")
            WebUI(router).run()
        else:
            # Simple command-line interaction
            logger.info("Starting command-line interface...")
            print(f"Welcome to {config.get('app', {}).get('name', 'Qwen-Assist-2')}!")
            print("Type 'quit' or 'exit' to end the session.")
            
            messages = []
            while True:
                user_input = input("\nUser: ")
                if user_input.lower() in ["quit", "exit"]:
                    print("Goodbye!")
                    break
                
                # Add user message to history
                messages.append({"role": "user", "content": user_input})
                
                # Get routing decision
                router_result = router.route(user_input, history=messages)
                print(f"\nRouting to: {router_result['agent']} (Confidence: {router_result.get('confidence', 'medium')})")
                print(f"Reason: {router_result['reason']}")
                
                # Get response from router
                print("\nAssistant: ", end="")
                response_text = ""
                for response in router.run(messages=messages):
                    response_text = typewriter_print(response, response_text, return_only=True)
                    print("\r" + " " * 100, end="")  # Clear line
                    print(f"\rAssistant: {response_text}", end="")
                print()
                
                # Add assistant response to history
                if response:
                    messages.extend(response)
                
    except Exception as e:
        logger.error(f"Error running Qwen-Assist-2: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Qwen-Assist-2: Multi-agent system built on the Qwen3 LLM")
    parser.add_argument("--config", "-c", type=str, help="Path to configuration file")
    parser.add_argument("--gui", "-g", action="store_true", help="Launch with Gradio UI")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    main(config_path=args.config, use_gui=args.gui)