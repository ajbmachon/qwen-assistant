"""Router agent for Qwen-Assist-2.

This agent is responsible for routing user queries to the appropriate specialized agent.
"""

import logging
from typing import Dict, Any, List, Optional, Iterator, Union
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
4. If multiple agents are needed, break down the task and route each subtask appropriately

Always respond in the following JSON format:
{
  "agent": "agent_name",
  "reason": "brief explanation of why this agent was chosen",
  "reformulated_query": "the original query, possibly reformulated for clarity"
}

Where agent_name is one of: "documentation", "search", "desktop", "data", or "router" (if you can handle it directly).
"""

class RouterAgent(BaseAgent):
    """Router agent responsible for directing queries to specialized agents."""
    
    def __init__(
        self,
        name: str = "Router Agent",
        description: str = "Routes queries to specialized agents",
        llm_config: Optional[Dict[str, Any]] = None,
        mcp_config: Optional[Dict[str, Any]] = None,
        system_message: str = ROUTER_SYSTEM_MESSAGE,
        files: Optional[List[str]] = None
    ):
        """Initialize the router agent.
        
        Args:
            name: Agent name.
            description: Short description of the agent.
            llm_config: Configuration for the LLM.
            mcp_config: Configuration for MCP servers.
            system_message: System message for the agent. Defaults to ROUTER_SYSTEM_MESSAGE.
            files: List of files to provide to the agent.
        """
        super().__init__(
            name=name,
            description=description,
            llm_config=llm_config or {},
            mcp_config=mcp_config or {},
            system_message=system_message,
            files=files or []
        )
        
        logger.info("Router Agent initialized")
    
    def route(
        self, 
        query: str, 
        history: Optional[List[Message]] = None
    ) -> Dict[str, Any]:
        """Route a query to the appropriate agent.
        
        Args:
            query: User query to route.
            history: Optional conversation history.
            
        Returns:
            Routing decision with agent, reason, and reformulated query.
        """
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
                        import json
                        import re
                        
                        # Extract JSON if it's embedded in a markdown code block
                        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
                        if json_match:
                            json_str = json_match.group(1)
                        else:
                            json_str = content
                            
                        routing_result = json.loads(json_str)
                        logger.info(f"Routing query to: {routing_result.get('agent')}")
                    except (json.JSONDecodeError, AttributeError) as e:
                        logger.error(f"Failed to parse routing response: {e}")
                        routing_result = {
                            "agent": "router",
                            "reason": "Failed to parse routing decision",
                            "reformulated_query": query
                        }
        
        if not routing_result:
            logger.warning("No routing decision made, defaulting to router agent")
            routing_result = {
                "agent": "router",
                "reason": "No routing decision available",
                "reformulated_query": query
            }
            
        return routing_result