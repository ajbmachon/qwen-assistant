"""Gradio-based UI for Qwen-Assist-2."""

import gradio as gr
import logging
from typing import Dict, Any, List, Callable, Union, Optional
from ..agents.base import BaseAgent
from qwen_agent.utils.output_beautify import typewriter_print
from qwen_agent.llm.schema import Message

logger = logging.getLogger(__name__)

class GradioInterface:
    """Gradio-based user interface for interacting with agents."""
    
    def __init__(
        self,
        primary_agent: BaseAgent,
        agent_map: Optional[Dict[str, BaseAgent]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the Gradio interface.
        
        Args:
            primary_agent: The main agent to interact with.
            agent_map: Dictionary mapping agent names to agent instances.
            config: UI configuration.
        """
        self.primary_agent = primary_agent
        self.agent_map = agent_map or {}
        self.config = config or {}
        
        # Add primary agent to agent map if not already there
        if primary_agent.name not in self.agent_map:
            self.agent_map[primary_agent.name] = primary_agent
        
        self.message_history: List[Message] = []
        
        logger.info("Gradio interface initialized")
    
    def _agent_response_generator(
        self,
        agent: BaseAgent,
        message: str
    ) -> str:
        """Generate responses from an agent.
        
        Args:
            agent: Agent to generate responses from.
            message: User message.
            
        Yields:
            Incremental agent response text.
        """
        # Add user message to history
        self.message_history.append({"role": "user", "content": message})
        
        # Get streaming response
        response_text = ""
        for response in agent.run(messages=self.message_history):
            response_text = typewriter_print(response, response_text, return_only=True)
            yield response_text
        
        # Update history with final response
        if response:
            self.message_history.extend(response)
    
    def _create_interface(self) -> gr.Blocks:
        """Create the Gradio interface.
        
        Returns:
            Gradio Blocks interface.
        """
        with gr.Blocks(
            title=self.config.get("title", "Qwen-Assist"),
            theme=self.config.get("theme", "default")
        ) as interface:
            with gr.Row():
                gr.Markdown(f"# {self.config.get('title', 'Qwen-Assist-2')}")
            
            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(
                        height=600,
                        show_label=False,
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            show_label=False,
                            placeholder="Type your message here...",
                            container=False,
                            scale=8
                        )
                        submit_btn = gr.Button("Send", scale=1)
                    
                    with gr.Row():
                        clear_btn = gr.Button("Clear History")
                
                with gr.Column(scale=1):
                    gr.Markdown("### Active Agents")
                    with gr.Accordion("Agents", open=True):
                        agent_info = gr.Markdown(
                            "\n".join([
                                f"- **{agent.name}**: {agent.description}"
                                for agent in self.agent_map.values()
                            ])
                        )
            
            def respond(message, history):
                history.append([message, ""])
                for response in self._agent_response_generator(self.primary_agent, message):
                    history[-1][1] = response
                    yield history, ""
            
            def clear_history():
                self.message_history = []
                return [], ""
            
            msg.submit(
                respond, 
                inputs=[msg, chatbot], 
                outputs=[chatbot, msg]
            )
            
            submit_btn.click(
                respond, 
                inputs=[msg, chatbot], 
                outputs=[chatbot, msg]
            )
            
            clear_btn.click(
                clear_history,
                outputs=[chatbot, msg]
            )
            
        return interface
    
    def launch(self) -> None:
        """Launch the Gradio interface."""
        interface = self._create_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=self.config.get("port", 7860),
            share=self.config.get("share", False)
        )