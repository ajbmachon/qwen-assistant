"""Documentation agent for Qwen-Assist-2.

This agent is responsible for handling library and API documentation queries
using the Context7 MCP.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from .base import BaseAgent

logger = logging.getLogger(__name__)

DOCUMENTATION_SYSTEM_MESSAGE = """You are a Documentation Agent specialized in providing accurate and helpful information about libraries, frameworks, APIs, and technical documentation.

Your primary role is to assist users with:
1. Finding documentation for specific libraries and packages
2. Explaining API usage and function parameters
3. Providing code examples and implementation guidance
4. Clarifying technical concepts from official documentation

When using the Context7 MCP, always follow this workflow:
1. First, resolve the library name to a valid Context7 ID using `mcp__context7__resolve-library-id`
2. Then, fetch the documentation using `mcp__context7__get-library-docs`
3. Format and present the information in a clear, well-structured manner
4. Include relevant code examples where available
5. Always cite the source and version of documentation

When responding:
- Be concise and focused on the user's specific documentation needs
- Present information with proper formatting, using code blocks for code examples
- Provide direct answers to questions when possible
- Suggest related functionality that might be helpful
- If documentation is unclear or unavailable, acknowledge limitations transparently

Use your knowledge to provide accurate, up-to-date, and helpful responses to technical documentation queries.
"""

class DocumentationAgent(BaseAgent):
    """Documentation agent for handling library and API documentation requests."""
    
    def __init__(
        self,
        name: str = "Documentation Agent",
        description: str = "Provides information about libraries, APIs, and technical documentation",
        llm_config: Optional[Dict[str, Any]] = None,
        mcp_config: Optional[Dict[str, Any]] = None,
        system_message: str = DOCUMENTATION_SYSTEM_MESSAGE,
        files: Optional[List[str]] = None,
        supported_libraries: Optional[Set[str]] = None
    ):
        """Initialize the documentation agent.
        
        Args:
            name: Agent name.
            description: Short description of the agent.
            llm_config: Configuration for the LLM.
            mcp_config: Configuration for MCP servers.
            system_message: System message for the agent. Defaults to DOCUMENTATION_SYSTEM_MESSAGE.
            files: List of files to provide to the agent.
            supported_libraries: Set of libraries this agent has specific knowledge about.
        """
        # Ensure mcp_config has context7 if it's provided
        if mcp_config and "context7" not in mcp_config:
            logger.warning("Context7 MCP not found in configuration, DocumentationAgent may not function properly")
        
        super().__init__(
            name=name,
            description=description,
            llm_config=llm_config or {},
            mcp_config=mcp_config or {},
            system_message=system_message,
            files=files or []
        )
        
        # Keep track of supported libraries for filtering or specialization
        self.supported_libraries = supported_libraries or set()
        
        logger.info("Documentation Agent initialized with Context7 MCP")
        if supported_libraries:
            logger.info(f"Agent has specialized knowledge of {len(supported_libraries)} libraries")
    
    def resolve_library(self, library_name: str) -> Optional[str]:
        """Resolve a library name to a Context7-compatible library ID.
        
        Args:
            library_name: Name of the library to resolve.
            
        Returns:
            The resolved library ID, or None if resolution failed.
        """
        logger.debug(f"Resolving library ID for: {library_name}")
        
        messages = [
            {"role": "user", "content": f"Please resolve the library ID for {library_name} using Context7."}
        ]
        
        for response in self.run(messages=messages):
            if response and len(response) > 0 and "content" in response[-1]:
                # Extract the content from the last message in the response
                return response[-1]["content"]
        
        return None
    
    def get_documentation(self, library_id: str, topic: Optional[str] = None, max_tokens: int = 10000) -> Optional[str]:
        """Get documentation for a specific library.
        
        Args:
            library_id: Context7-compatible library ID.
            topic: Optional topic to focus documentation on.
            max_tokens: Maximum number of tokens of documentation to retrieve.
            
        Returns:
            The retrieved documentation, or None if retrieval failed.
        """
        logger.debug(f"Fetching documentation for library ID: {library_id}" + 
                    (f" on topic: {topic}" if topic else ""))
        
        # Create a message asking for documentation
        content = f"Please provide documentation for the library with ID: {library_id}"
        if topic:
            content += f", focusing on the topic: {topic}"
        
        messages = [
            {"role": "user", "content": content}
        ]
        
        for response in self.run(messages=messages):
            if response and len(response) > 0 and "content" in response[-1]:
                # Extract the content from the last message in the response
                return response[-1]["content"]
        
        return None
    
    def is_documentation_query(self, query: str) -> bool:
        """Determine if a query is likely asking for documentation.
        
        Args:
            query: The user query to analyze.
            
        Returns:
            True if the query appears to be asking for documentation, False otherwise.
        """
        # Simple heuristic - could be improved with more sophisticated methods
        documentation_keywords = [
            "documentation", "docs", "api", "library", "package", "module",
            "function", "method", "class", "interface", "parameter", "argument",
            "example", "usage", "how to use", "reference"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in documentation_keywords)
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'DocumentationAgent':
        """Create a documentation agent from a configuration dictionary.
        
        Args:
            config: Configuration dictionary.
            
        Returns:
            Initialized documentation agent.
        """
        # Extract documentation-specific config if present
        doc_config = config.get("documentation", {})
        
        # Extract supported libraries if specified
        supported_libraries = set(doc_config.get("supported_libraries", []))
        
        return cls(
            name=config.get("name", "Documentation Agent"),
            description=config.get("description", "Provides information about libraries, APIs, and technical documentation"),
            llm_config=config.get("llm", {}),
            mcp_config=config.get("mcp_servers", {}),
            system_message=doc_config.get("system_message", DOCUMENTATION_SYSTEM_MESSAGE),
            files=config.get("files", []),
            supported_libraries=supported_libraries
        )