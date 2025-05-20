"""Main entry point for the Qwen Multi-Assistant system."""
import argparse
import logging
import os
import sys

from .ui import launch_ui

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run() -> None:
    """Run the application from the command line."""
    parser = argparse.ArgumentParser(description="Qwen Multi-Assistant")
    parser.add_argument(
        "--config",
        help="Path to configuration file",
        default=os.environ.get("QWEN_CONFIG_PATH"),
    )
    args = parser.parse_args()

    try:
        launch_ui(args.config)
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:  # pragma: no cover - unexpected failures
        logger.exception(f"Unhandled exception: {e}")
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover - manual start
    run()

