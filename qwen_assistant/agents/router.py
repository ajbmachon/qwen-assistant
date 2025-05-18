"""Router agent for Qwen-Assist-2.

This agent is responsible for routing user queries to the appropriate specialized agent.
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Iterator, Set
from .base import BaseAgent
from qwen_agent.llm.schema import Message

logger = logging.getLogger(__name__)

ROUTER_SYSTEM_MESSAGE = """You are a Router Agent responsible for analyzing user queries and routing them to the most appropriate specialized agent. 

You have access to the following agents:
1. Documentation Agent (context7): For queries about libraries, frameworks, APIs, and technical documentation
2. Search Agent (exa): For web searches, current information, and general knowledge queries
3. Desktop Agent: For tasks that involve file system operations, running commands, and local system interactions
4. Data Agent (airtable): For data operations, database queries, and structured data analysis

Your job is to:
1. Understand the user's intent
2. Determine which agent is best suited to handle the query
3. Route the query to that agent
4. If multiple agents are needed, select the primary agent for the initial handling

Always respond in the following JSON format:
{
  "agent": "agent_name",
  "reason": "brief explanation of why this agent was chosen",
  "reformulated_query": "the original query, possibly reformulated for clarity",
  "confidence": "high/medium/low"
}

Where agent_name is one of: "documentation", "search", "desktop", "data", or "router" (if you can handle it directly).
"""

# Mapping of agent names to their capabilities
AGENT_CAPABILITIES = {
    "documentation": [
        "library documentation", "api reference", "code examples", 
        "programming tutorials", "framework guides", "sdk usage"
    ],
    "search": [
        "web search", "current events", "general knowledge", "facts", 
        "latest information", "news", "research papers"
    ],
    "desktop": [
        "file operations", "system commands", "local applications", 
        "file search", "directory listing", "file editing"
    ],
    "data": [
        "database queries", "data analysis", "spreadsheets", 
        "data visualization", "data extraction", "structured data"
    ],
    "router": [
        "simple questions", "conversational queries", "clarification", 
        "agent capabilities", "help requests"
    ]
}

class RouterAgent(BaseAgent):
    """Router agent responsible for directing queries to specialized agents."""
    
    def __init__(
        self,
        name: str = "Router Agent",
        description: str = "Routes queries to specialized agents",
        llm_config: Optional[Dict[str, Any]] = None,
        mcp_config: Optional[Dict[str, Any]] = None,
        system_message: str = ROUTER_SYSTEM_MESSAGE,
        files: Optional[List[str]] = None,
        available_agents: Optional[Set[str]] = None
    ):
        """Initialize the router agent.
        
        Args:
            name: Agent name.
            description: Short description of the agent.
            llm_config: Configuration for the LLM.
            mcp_config: Configuration for MCP servers.
            system_message: System message for the agent. Defaults to ROUTER_SYSTEM_MESSAGE.
            files: List of files to provide to the agent.
            available_agents: Set of available agent names for routing.
        """
        super().__init__(
            name=name,
            description=description,
            llm_config=llm_config or {},
            mcp_config=mcp_config or {},
            system_message=system_message,
            files=files or []
        )
        
        # Set of available agents for routing
        self.available_agents = available_agents or {"documentation", "search", "desktop", "data", "router"}
        
        # Update system message with available agents
        if available_agents and available_agents != {"documentation", "search", "desktop", "data", "router"}:
            updated_system = self._customize_system_message(system_message, available_agents)
            self.agent.update_system_message(updated_system)
        
        logger.info(f"Router Agent initialized with available agents: {self.available_agents}")
    
    def _customize_system_message(self, system_message: str, available_agents: Set[str]) -> str:
        """Customize the system message based on available agents.
        
        Args:
            system_message: Original system message.
            available_agents: Set of available agent names.
            
        Returns:
            Updated system message.
        """
        # Extract the agents section from the system message
        agents_section_pattern = r"You have access to the following agents:(.*?)Your job is to:"
        agents_section_match = re.search(agents_section_pattern, system_message, re.DOTALL)
        
        if not agents_section_match:
            return system_message
        
        agents_section = agents_section_match.group(1)
        agent_lines = agents_section.strip().split("\n")
        
        # Filter the agent lines based on available agents
        filtered_lines = []
        for line in agent_lines:
            for agent in available_agents:
                if agent in line.lower():
                    filtered_lines.append(line)
                    break
        
        # Replace the agents section in the system message
        updated_agents_section = "\nYou have access to the following agents:\n" + "\n".join(filtered_lines) + "\n\nYour job is to:"
        updated_system = re.sub(agents_section_pattern, updated_agents_section, system_message, flags=re.DOTALL)
        
        return updated_system
    
    def route(
        self, 
        query: str, 
        history: Optional[List[Message]] = None,
        default_agent: str = "router"
    ) -> Dict[str, Any]:
        """Route a query to the appropriate agent.
        
        Args:
            query: User query to route.
            history: Optional conversation history.
            default_agent: Default agent if routing fails.
            
        Returns:
            Routing decision with agent, reason, and reformulated query.
        """
        if not query.strip():
            logger.warning("Empty query received, defaulting to router agent")
            return {
                "agent": default_agent,
                "reason": "Empty query received",
                "reformulated_query": query,
                "confidence": "high"
            }
        
        messages = history or []
        messages.append({"role": "user", "content": query})
        
        routing_result = {}
        for response in self.run(messages=messages):
            # Extract final response content
            if response and response[-1]["role"] == "assistant":
                content = response[-1]["content"]
                if isinstance(content, str):
                    # Try to parse JSON from the response
                    try:
                        # Extract JSON if it's embedded in a markdown code block
                        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
                        if json_match:
                            json_str = json_match.group(1)
                        else:
                            json_str = content
                            
                        routing_result = json.loads(json_str)
                        
                        # Validate the result
                        if self._validate_routing_result(routing_result):
                            logger.info(f"Routing query to: {routing_result.get('agent')} with confidence: {routing_result.get('confidence', 'medium')}")
                        else:
                            logger.warning(f"Invalid routing result: {routing_result}, using default agent: {default_agent}")
                            routing_result = self._get_default_routing(query, default_agent)
                    except (json.JSONDecodeError, AttributeError) as e:
                        logger.error(f"Failed to parse routing response: {e}")
                        routing_result = self._get_default_routing(query, default_agent)
        
        if not routing_result:
            logger.warning(f"No routing decision made, defaulting to {default_agent} agent")
            routing_result = self._get_default_routing(query, default_agent)
            
        return routing_result
    
    def _validate_routing_result(self, result: Dict[str, Any]) -> bool:
        """Validate the routing result.
        
        Args:
            result: Routing result to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        required_keys = {"agent", "reason", "reformulated_query"}
        if not all(key in result for key in required_keys):
            return False
        
        agent = result.get("agent", "").lower()
        if agent not in self.available_agents:
            return False
        
        return True
    
    def _get_default_routing(self, query: str, default_agent: str) -> Dict[str, Any]:
        """Get default routing decision when routing fails.
        
        Args:
            query: Original user query.
            default_agent: Default agent name.
            
        Returns:
            Default routing decision.
        """
        return {
            "agent": default_agent,
            "reason": "Fallback to default agent",
            "reformulated_query": query,
            "confidence": "low"
        }
    
    def get_available_agents(self) -> Set[str]:
        """Get the set of available agents for routing.
        
        Returns:
            Set of available agent names.
        """
        return self.available_agents.copy()
    
    def register_agent(self, agent_name: str) -> None:
        """Register a new agent for routing.
        
        Args:
            agent_name: Name of the agent to register.
        """
        if agent_name not in self.available_agents:
            self.available_agents.add(agent_name)
            logger.info(f"Registered new agent: {agent_name}")
    
    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent from routing.
        
        Args:
            agent_name: Name of the agent to unregister.
        """
        if agent_name in self.available_agents and agent_name != "router":
            self.available_agents.remove(agent_name)
            logger.info(f"Unregistered agent: {agent_name}")
        else:
            logger.warning(f"Cannot unregister agent: {agent_name}")
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'RouterAgent':
        """Create a router agent from a configuration dictionary.
        
        Args:
            config: Configuration dictionary.
            
        Returns:
            Initialized router agent.
        """
        router_config = config.get("routing", {})
        available_agents = set(router_config.get("available_agents", ["documentation", "search", "desktop", "data", "router"]))
        
        return cls(
            name=config.get("name", "Router Agent"),
            description=config.get("description", "Routes queries to specialized agents"),
            llm_config=config.get("llm", {}),
            mcp_config=config.get("mcp_servers", {}),
            system_message=router_config.get("system_message", ROUTER_SYSTEM_MESSAGE),
            files=config.get("files", []),
            available_agents=available_agents
        )