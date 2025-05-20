import asyncio
import logging
from typing import Optional

import gradio as gr

from .config import load_config
from .agents.desktop import DesktopAgent

logger = logging.getLogger(__name__)


class AssistantUI:
    """Simple wrapper to run the DesktopAgent with Gradio chat interface."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = load_config(config_path)
        desktop_cfg = self.config["agents"]["desktop"]
        model_cfg = self.config["models"]["agent"]
        self.agent = DesktopAgent(desktop_cfg, model_cfg)

    async def prepare(self):
        await self.agent.prepare()

    async def cleanup(self):
        await self.agent.cleanup()

    async def _respond(self, message: str, history: list[tuple[str, str]]):
        request = {"query": message}
        response = await self.agent.handle_request(request, {})
        if response.get("success"):
            return response.get("message", "")
        return f"Error: {response.get('message', 'unknown error')}"

    def launch(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.prepare())

        chat = gr.ChatInterface(self._respond, title=self.config["ui"].get("title", "Qwen Multi-Assistant"))
        chat.launch(server_port=self.config["ui"].get("port", 7860), share=False)

        loop.run_until_complete(self.cleanup())


def launch_ui(config_path: Optional[str] = None) -> None:
    """Entry point to start the Gradio UI."""
    ui = AssistantUI(config_path)
    ui.launch()
