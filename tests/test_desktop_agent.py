"""
Tests for the Desktop Agent implementation.
"""
import pytest
import pytest_asyncio
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import json

from qwen_assistant.agents.desktop import DesktopAgent


@pytest.fixture
def desktop_agent_config():
    """Desktop agent configuration fixture."""
    return {
        "mcp_endpoint": "http://localhost:9000",
        "timeout": 30
    }


@pytest.fixture
def model_config():
    """Model configuration fixture."""
    return {
        "model": "qwen3-32b",
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 0.9
    }


@pytest.fixture
def desktop_agent(desktop_agent_config, model_config):
    """Create a desktop agent for testing."""
    agent = DesktopAgent(desktop_agent_config, model_config)
    return agent


class TestDesktopAgent:
    """Test suite for Desktop Agent."""

    def test_initialization(self, desktop_agent, desktop_agent_config, model_config):
        """Test agent initialization."""
        assert desktop_agent.mcp_endpoint == desktop_agent_config["mcp_endpoint"]
        assert desktop_agent.config == desktop_agent_config
        assert desktop_agent.model_config == model_config
        assert desktop_agent.name == "DesktopAgent"
        assert "file system" in desktop_agent.description.lower()

    def test_capabilities(self, desktop_agent):
        """Test agent capabilities."""
        capabilities = desktop_agent.capabilities
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert "Execute terminal commands" in capabilities
        assert "Read and write files" in capabilities
        assert "Search for files and code" in capabilities

    @pytest.mark.parametrize(
        "query,expected_confidence",
        [
            ("run command ls", 0.4),
            ("search files in the src directory", 0.4),
            ("write a new file", 0.4),
            ("what's the weather today", 0.0),
            ("tell me a joke", 0.0),
        ],
    )
    def test_can_handle(self, desktop_agent, query, expected_confidence):
        """Test agent's ability to determine if it can handle a request."""
        confidence = desktop_agent.can_handle({"query": query})
        assert confidence == expected_confidence

    @pytest.mark.asyncio
    async def test_handle_request_execute_command(self, desktop_agent):
        """Test handling execute command request."""
        with patch.object(desktop_agent, "execute_command", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {"success": True, "output": "command output"}
            
            request = {"query": "run ls -la", "action": "execute_command", "command": "ls -la"}
            context = {}
            
            response = await desktop_agent.handle_request(request, context)
            
            assert response["success"] is True
            assert response["agent"] == "DesktopAgent"
            assert "Executed command" in response["message"]
            mock_execute.assert_called_once_with("ls -la")

    @pytest.mark.asyncio
    async def test_handle_request_read_file(self, desktop_agent):
        """Test handling read file request."""
        with patch.object(desktop_agent, "read_file", new_callable=AsyncMock) as mock_read:
            mock_read.return_value = {"success": True, "content": "file content"}
            
            request = {"query": "read file.txt", "action": "read_file", "file_path": "file.txt"}
            context = {}
            
            response = await desktop_agent.handle_request(request, context)
            
            assert response["success"] is True
            assert "Read file" in response["message"]
            mock_read.assert_called_once_with("file.txt")

    @pytest.mark.asyncio
    async def test_mcp_call(self, desktop_agent):
        """Test MCP API call."""
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {"success": True, "result": "test result"}
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await desktop_agent._mcp_call("test_tool", {"param": "value"})
            
            assert result["success"] is True
            assert result["result"] == "test result"
            mock_post.assert_called_once()