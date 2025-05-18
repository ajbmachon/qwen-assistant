"""Base agent class for Qwen-Assist-2."""

from typing import Dict, Any, List, Optional, Iterator, Union
import logging
from qwen_agent.agents import Assistant
from qwen_agent.llm import BaseChatModel, get_chat_model
from qwen_agent.llm.schema import Message

logger = logging.getLogger(__name__)

class BaseAgent:
    """Base agent class for all Qwen-Assist-2 agents."""
    
    def __init__(
        self,
        name: str,
        description: str,
        llm_config: Dict[str, Any],
        mcp_config: Optional[Dict[str, Any]] = None,
        system_message: Optional[str] = None,
        files: Optional[List[str]] = None
    ):
        """Initialize the base agent.
        
        Args:
            name: Agent name.
            description: Short description of the agent.
            llm_config: Configuration for the LLM.
            mcp_config: Configuration for MCP servers.
            system_message: System message for the agent.
            files: List of files to provide to the agent.
        """
        self.name = name
        self.description = description
        self.llm_config = llm_config
        self.mcp_config = mcp_config or {}
        
        # Format tools for Qwen-Agent
        function_list = []
        if self.mcp_config:
            function_list.append({"mcpServers": self.mcp_config})
        
        # Initialize the Qwen-Agent Assistant
        self.agent = Assistant(
            llm=self.llm_config,
            system_message=system_message,
            function_list=function_list,
            files=files or []
        )
        
        logger.info(f"Initialized agent: {self.name}")
    
    def run(
        self, 
        messages: List[Message], 
        **kwargs
    ) -> Iterator[List[Message]]:
        """Run the agent with the given messages.
        
        Args:
            messages: List of messages to process.
            **kwargs: Additional arguments to pass to the agent.
            
        Returns:
            Iterator of response messages.
        """
        logger.debug(f"Running agent {self.name} with {len(messages)} messages")
        return self.agent.run(messages=messages, **kwargs)
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'BaseAgent':
        """Create an agent from a configuration dictionary.
        
        Args:
            config: Configuration dictionary.
            
        Returns:
            Initialized agent.
        """
        llm_config = config.get("llm", {})
        mcp_servers = config.get("mcp_servers", {})
        
        return cls(
            name=config.get("name", "Unnamed Agent"),
            description=config.get("description", ""),
            llm_config=llm_config,
            mcp_config=mcp_servers,
            system_message=config.get("system_message"),
            files=config.get("files")
        )