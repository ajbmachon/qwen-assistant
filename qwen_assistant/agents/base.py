"""
Base agent class for all specialized agents in the Qwen Multi-Assistant system.
All specialized agents inherit from this class to ensure consistent interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseAgent(ABC):
    """Base class for all specialized agents in the Qwen Multi-Assistant system."""
    
    def __init__(self, config: Dict[str, Any], model_config: Dict[str, Any]):
        """
        Initialize the base agent.
        
        Args:
            config: Agent-specific configuration
            model_config: LLM model configuration
        """
        self.config = config
        self.model_config = model_config
        self.name = self.__class__.__name__
        self.description = "Base agent for Qwen Multi-Assistant"
        
    @abstractmethod
    async def handle_request(self, request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user request with the given context.
        
        Args:
            request: The user request information
            context: Context information from previous interactions
            
        Returns:
            Dict containing the agent's response
        """
        pass
    
    @property
    def capabilities(self) -> List[str]:
        """
        Return a list of capabilities this agent can perform.
        
        Returns:
            List of capability descriptions
        """
        return []
    
    def can_handle(self, request: Dict[str, Any]) -> float:
        """
        Determine if this agent can handle the given request and with what confidence.
        
        Args:
            request: The user request to evaluate
            
        Returns:
            Confidence score (0.0 to 1.0) for this agent's ability to handle the request
        """
        return 0.0
    
    async def prepare(self):
        """Perform any necessary setup or preparation before handling requests."""
        pass
    
    async def cleanup(self):
        """Perform any necessary cleanup after handling requests."""
        pass