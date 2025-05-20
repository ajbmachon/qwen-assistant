"""
Desktop Agent implementation for the Qwen Multi-Assistant system.
This agent handles file system and local machine operations using DesktopCommanderMCP.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp

from .base import BaseAgent

logger = logging.getLogger(__name__)


class DesktopAgent(BaseAgent):
    """
    Desktop Agent for handling file system and local machine operations using DesktopCommanderMCP.

    Capabilities:
    - Execute terminal commands
    - Read and write files
    - Search for files and code
    - List directories and files
    - Get file metadata
    """

    def __init__(self, config: Dict[str, Any], model_config: Dict[str, Any]):
        """
        Initialize the Desktop Agent.

        Args:
            config: Agent-specific configuration including MCP server endpoint
            model_config: LLM model configuration
        """
        super().__init__(config, model_config)
        self.description = "Agent for file system and local machine operations"
        self.mcp_endpoint = config.get("mcp_endpoint", "http://localhost:9000")
        self.session = None

    async def prepare(self):
        """Initialize HTTP session for API calls."""
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Clean up HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    @property
    def capabilities(self) -> List[str]:
        """Return the capabilities of the Desktop Agent."""
        return [
            "Execute terminal commands",
            "Read and write files",
            "Search for files and code",
            "List directories and files",
            "Get file metadata",
        ]

    def can_handle(self, request: Dict[str, Any]) -> float:
        """
        Determine if this agent can handle the given request and with what confidence.

        Args:
            request: The user request to evaluate

        Returns:
            Confidence score (0.0 to 1.0) for handling the request
        """
        # Keywords that suggest this agent should handle the request
        desktop_keywords = {
            # High confidence keywords (0.4)
            "high": [
                "run command",
                "execute command",
                "terminal command",
                "shell command",
                "system command",
                "search files",
                "list directory",
                "write file",
                "read file",
                "create file",
                "edit file",
                "delete file",
                "rename file",
            ],
            # Medium confidence keywords (0.2)
            "medium": [
                "file",
                "directory",
                "folder",
                "command",
                "terminal",
                "shell",
                "run",
                "execute",
                "script",
                "find",
                "code",
                "local",
                "computer",
            ],
        }

        query = request.get("query", "").lower()
        confidence = 0.0

        # Check for high confidence keywords first
        for keyword in desktop_keywords["high"]:
            if keyword in query:
                confidence += 0.4
                break
        else:
            # Additional check for phrases like "write ... file"
            if "write" in query and "file" in query:
                confidence += 0.4

        # If no high confidence keywords found, check medium ones
        if confidence == 0.0:
            for keyword in desktop_keywords["medium"]:
                if keyword in query:
                    confidence += 0.2

        # Cap confidence at 1.0
        return min(confidence, 1.0)

    async def _mcp_call(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a call to the DesktopCommanderMCP server.

        Args:
            tool_name: Name of the MCP tool to call
            params: Parameters for the tool

        Returns:
            Response from the MCP server
        """
        if not self.session:
            await self.prepare()

        try:
            payload = {"tool": tool_name, "params": params}

            post_result = self.session.post(
                f"{self.mcp_endpoint}/api/v1/execute", json=payload
            )

            if asyncio.iscoroutine(post_result):
                response_ctx = await post_result
            else:
                response_ctx = post_result

            async with response_ctx as response:
                result = await response.json()
                return result
        except Exception as e:
            logger.error(f"Error calling DesktopCommanderMCP: {e}")
            return {"error": str(e), "success": False}

    async def execute_command(self, command: str) -> Dict[str, Any]:
        """
        Execute a terminal command.

        Args:
            command: Command to execute

        Returns:
            Command execution result
        """
        return await self._mcp_call("execute_command", {"command": command})

    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read the contents of a file.

        Args:
            file_path: Path to the file to read

        Returns:
            File contents
        """
        return await self._mcp_call("read_file", {"path": file_path})

    async def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Write content to a file.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file

        Returns:
            Result of the write operation
        """
        return await self._mcp_call(
            "write_file", {"path": file_path, "content": content}
        )

    async def search_files(self, directory: str, pattern: str) -> Dict[str, Any]:
        """
        Search for files matching a pattern.

        Args:
            directory: Directory to search in
            pattern: Pattern to search for

        Returns:
            List of matching files
        """
        return await self._mcp_call(
            "search_files", {"directory": directory, "pattern": pattern}
        )

    async def search_code(self, directory: str, query: str) -> Dict[str, Any]:
        """
        Search code for a specific pattern.

        Args:
            directory: Directory to search in
            query: Code pattern to search for

        Returns:
            Search results
        """
        return await self._mcp_call(
            "search_code", {"directory": directory, "query": query}
        )

    async def list_directory(self, directory: str) -> Dict[str, Any]:
        """
        List contents of a directory.

        Args:
            directory: Path to directory

        Returns:
            Directory contents
        """
        return await self._mcp_call("list_directory", {"path": directory})

    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get metadata for a file.

        Args:
            file_path: Path to file

        Returns:
            File metadata
        """
        return await self._mcp_call("get_file_info", {"path": file_path})

    async def handle_request(
        self, request: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a user request with the given context.

        Args:
            request: The user request information
            context: Context information from previous interactions

        Returns:
            Dict containing the agent's response
        """
        query = request.get("query", "")
        action = request.get("action", "")

        # Initialize the response
        response = {
            "agent": "DesktopAgent",
            "success": False,
            "message": "",
            "data": None,
        }

        try:
            # Handle different actions based on the query and context
            if action == "execute_command" or "run" in query or "execute" in query:
                command = request.get("command", "")
                if not command:
                    # Try to extract command from query
                    command = query.replace("run", "").replace("execute", "").strip()

                result = await self.execute_command(command)
                response["success"] = result.get("success", False)
                response["data"] = result
                response["message"] = f"Executed command: {command}"

            elif action == "read_file" or "read" in query:
                file_path = request.get("file_path", "")
                if not file_path:
                    response["message"] = "No file path provided"
                else:
                    result = await self.read_file(file_path)
                    response["success"] = result.get("success", False)
                    response["data"] = result
                    response["message"] = f"Read file: {file_path}"

            elif action == "write_file" or "write" in query or "save" in query:
                file_path = request.get("file_path", "")
                content = request.get("content", "")
                if not file_path or not content:
                    response["message"] = "File path or content not provided"
                else:
                    result = await self.write_file(file_path, content)
                    response["success"] = result.get("success", False)
                    response["data"] = result
                    response["message"] = f"Wrote to file: {file_path}"

            elif (
                action == "search_files"
                or "find files" in query
                or "search files" in query
            ):
                directory = request.get("directory", ".")
                pattern = request.get("pattern", "")
                if not pattern:
                    response["message"] = "No search pattern provided"
                else:
                    result = await self.search_files(directory, pattern)
                    response["success"] = result.get("success", False)
                    response["data"] = result
                    response["message"] = f"Searched for files: {pattern}"

            elif (
                action == "search_code"
                or "find code" in query
                or "search code" in query
            ):
                directory = request.get("directory", ".")
                query_text = request.get("code_query", "")
                if not query_text:
                    response["message"] = "No code search query provided"
                else:
                    result = await self.search_code(directory, query_text)
                    response["success"] = result.get("success", False)
                    response["data"] = result
                    response["message"] = f"Searched code for: {query_text}"

            elif action == "list_directory" or "list" in query or "ls" in query:
                directory = request.get("directory", ".")
                result = await self.list_directory(directory)
                response["success"] = result.get("success", False)
                response["data"] = result
                response["message"] = f"Listed directory: {directory}"

            elif action == "get_file_info" or "file info" in query:
                file_path = request.get("file_path", "")
                if not file_path:
                    response["message"] = "No file path provided"
                else:
                    result = await self.get_file_info(file_path)
                    response["success"] = result.get("success", False)
                    response["data"] = result
                    response["message"] = f"Got info for file: {file_path}"

            else:
                # General processing of query using LLM
                # This would require integration with the Qwen LLM for more complex queries
                response["message"] = f"Processing desktop request: {query}"
                # Default handling could involve analyzing the query and determining which operation to perform

        except Exception as e:
            logger.exception(f"Error handling desktop request: {e}")
            response["success"] = False
            response["message"] = f"Error processing request: {str(e)}"

        return response
