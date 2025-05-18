"""Search agent for Qwen-Assist-2.

This agent is responsible for handling web searches and content retrieval
using the Exa MCP.
"""

import logging
from typing import Dict, Any, List, Optional, Iterator, Union
from .base import BaseAgent

logger = logging.getLogger(__name__)

SEARCH_SYSTEM_MESSAGE = """You are a Search Agent specialized in finding and analyzing information from the web.

Your primary role is to assist users with:
1. Finding up-to-date information from the web
2. Retrieving specific content from websites
3. Researching topics thoroughly and providing comprehensive answers
4. Finding research papers and academic information
5. Searching social media and company information

When using the Exa MCP, follow these guidelines:
1. For general web searches, use `mcp__exa__web_search_exa`
2. For academic research, use `mcp__exa__research_paper_search`
3. For social media content, use `mcp__exa__twitter_search`
4. For company research, use `mcp__exa__company_research`
5. For extracting content from specific URLs, use `mcp__exa__crawling`
6. For finding competitors, use `mcp__exa__competitor_finder`
7. For LinkedIn company information, use `mcp__exa__linkedin_search`

When responding:
- Always provide attribution for information sources
- Include relevant URLs to help users verify information
- Format your responses clearly with proper headings and structure
- When appropriate, synthesize information from multiple sources
- Be transparent about information gaps or limitations in search results
- Prioritize recent, authoritative sources when available

Use your capabilities to provide accurate, up-to-date, and well-sourced information in response to user queries.
"""

class SearchAgent(BaseAgent):
    """Search agent for handling web searches and content retrieval."""
    
    def __init__(
        self,
        name: str = "Search Agent",
        description: str = "Finds information from the web and retrieves content from websites",
        llm_config: Optional[Dict[str, Any]] = None,
        mcp_config: Optional[Dict[str, Any]] = None,
        system_message: str = SEARCH_SYSTEM_MESSAGE,
        files: Optional[List[str]] = None
    ):
        """Initialize the search agent.
        
        Args:
            name: Agent name.
            description: Short description of the agent.
            llm_config: Configuration for the LLM.
            mcp_config: Configuration for MCP servers.
            system_message: System message for the agent. Defaults to SEARCH_SYSTEM_MESSAGE.
            files: List of files to provide to the agent.
        """
        # Ensure mcp_config has exa if it's provided
        if mcp_config and "exa" not in mcp_config:
            logger.warning("Exa MCP not found in configuration, SearchAgent may not function properly")
        
        super().__init__(
            name=name,
            description=description,
            llm_config=llm_config or {},
            mcp_config=mcp_config or {},
            system_message=system_message,
            files=files or []
        )
        
        logger.info("Search Agent initialized with Exa MCP")

    def search_web(self, query: str, num_results: int = 5) -> Iterator[List[Dict[str, Any]]]:
        """Search the web for information.
        
        Args:
            query: The search query.
            num_results: Number of search results to return.
            
        Returns:
            Iterator of response messages.
        """
        logger.debug(f"Searching web for: {query}")
        
        messages = [
            {"role": "user", "content": f"Search the web for: {query}. Return {num_results} results."}
        ]
        
        return self.run(messages=messages)
    
    def search_research_papers(self, query: str, num_results: int = 5, max_characters: int = 3000) -> Iterator[List[Dict[str, Any]]]:
        """Search for research papers.
        
        Args:
            query: The search query.
            num_results: Number of research papers to return.
            max_characters: Maximum number of characters to return for each result's text content.
            
        Returns:
            Iterator of response messages.
        """
        logger.debug(f"Searching research papers for: {query}")
        
        messages = [
            {"role": "user", "content": f"Find research papers about: {query}. Return {num_results} results with maximum {max_characters} characters per result."}
        ]
        
        return self.run(messages=messages)
    
    def search_twitter(self, query: str, num_results: int = 5) -> Iterator[List[Dict[str, Any]]]:
        """Search Twitter/X for posts and accounts.
        
        Args:
            query: The search query.
            num_results: Number of Twitter results to return.
            
        Returns:
            Iterator of response messages.
        """
        logger.debug(f"Searching Twitter for: {query}")
        
        messages = [
            {"role": "user", "content": f"Search Twitter for: {query}. Return {num_results} results."}
        ]
        
        return self.run(messages=messages)
    
    def research_company(self, company_url: str, subpages: int = 10) -> Iterator[List[Dict[str, Any]]]:
        """Research a company by its website.
        
        Args:
            company_url: Company website URL.
            subpages: Number of subpages to crawl.
            
        Returns:
            Iterator of response messages.
        """
        logger.debug(f"Researching company: {company_url}")
        
        messages = [
            {"role": "user", "content": f"Research the company at {company_url}. Crawl up to {subpages} subpages."}
        ]
        
        return self.run(messages=messages)
    
    def extract_content(self, url: str) -> Iterator[List[Dict[str, Any]]]:
        """Extract content from a specific URL.
        
        Args:
            url: The URL to crawl.
            
        Returns:
            Iterator of response messages.
        """
        logger.debug(f"Extracting content from: {url}")
        
        messages = [
            {"role": "user", "content": f"Extract the content from this URL: {url}"}
        ]
        
        return self.run(messages=messages)
    
    def find_competitors(self, query: str, exclude_domain: Optional[str] = None, num_results: int = 10) -> Iterator[List[Dict[str, Any]]]:
        """Find competitors for a company.
        
        Args:
            query: Description of what the company does.
            exclude_domain: Optional company's website to exclude from results.
            num_results: Number of competitors to return.
            
        Returns:
            Iterator of response messages.
        """
        logger.debug(f"Finding competitors for: {query}")
        
        content = f"Find competitors for a company that {query}. Return {num_results} results."
        if exclude_domain:
            content += f" Exclude the domain {exclude_domain} from results."
        
        messages = [
            {"role": "user", "content": content}
        ]
        
        return self.run(messages=messages)
    
    def search_linkedin(self, query: str, num_results: int = 5) -> Iterator[List[Dict[str, Any]]]:
        """Search LinkedIn for companies.
        
        Args:
            query: The search query (company name or URL + "company page").
            num_results: Number of search results to return.
            
        Returns:
            Iterator of response messages.
        """
        logger.debug(f"Searching LinkedIn for: {query}")
        
        messages = [
            {"role": "user", "content": f"Search LinkedIn for: {query}. Return {num_results} results."}
        ]
        
        return self.run(messages=messages)
    
    def is_search_query(self, query: str) -> bool:
        """Determine if a query is likely asking for a search.
        
        Args:
            query: The user query to analyze.
            
        Returns:
            True if the query appears to be asking for a search, False otherwise.
        """
        # Simple heuristic - could be improved with more sophisticated methods
        search_keywords = [
            "search", "find", "look up", "google", "research", "information", 
            "data", "recent", "latest", "news", "article", "website", "source", 
            "what is", "who is", "where is", "when is", "why is"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in search_keywords)
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'SearchAgent':
        """Create a search agent from a configuration dictionary.
        
        Args:
            config: Configuration dictionary.
            
        Returns:
            Initialized search agent.
        """
        # Extract search-specific config if present
        search_config = config.get("search", {})
        
        return cls(
            name=config.get("name", "Search Agent"),
            description=config.get("description", "Finds information from the web and retrieves content from websites"),
            llm_config=config.get("llm", {}),
            mcp_config=config.get("mcp_servers", {}),
            system_message=search_config.get("system_message", SEARCH_SYSTEM_MESSAGE),
            files=config.get("files", [])
        )