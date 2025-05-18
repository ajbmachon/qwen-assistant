"""Tests for the router agent."""

import json
import pytest
from unittest.mock import patch, MagicMock
from qwen_assistant.agents.router import RouterAgent, ROUTER_SYSTEM_MESSAGE, AGENT_CAPABILITIES

def test_router_agent_init():
    """Test initialization of the router agent."""
    with patch("qwen_assistant.agents.base.Assistant") as mock_assistant:
        # Create router agent with minimal config
        agent = RouterAgent(
            llm_config={"model": "test-model"},
            mcp_config={}
        )
        
        # Assert instance created correctly
        assert agent.name == "Router Agent"
        assert "Routes queries" in agent.description
        assert agent.available_agents == {"documentation", "search", "desktop", "data", "router"}
        assert mock_assistant.called

def test_router_agent_with_custom_agents():
    """Test initialization with custom available agents."""
    with patch("qwen_assistant.agents.base.Assistant") as mock_assistant:
        # Mock assistant instance
        mock_instance = mock_assistant.return_value
        
        # Create router agent with custom agents
        agent = RouterAgent(
            llm_config={"model": "test-model"},
            available_agents={"documentation", "search", "custom"}
        )
        
        # Assert instance created correctly
        assert agent.available_agents == {"documentation", "search", "custom"}
        # Check if system message was updated
        assert mock_instance.update_system_message.called

def test_customize_system_message():
    """Test customization of system message based on available agents."""
    with patch("qwen_assistant.agents.base.Assistant"):
        agent = RouterAgent(llm_config={"model": "test-model"})
        
        # Test with subset of agents
        custom_message = agent._customize_system_message(
            ROUTER_SYSTEM_MESSAGE,
            {"documentation", "search"}
        )
        
        # Should only include documentation and search agent lines
        assert "Documentation Agent" in custom_message
        assert "Search Agent" in custom_message
        assert "Desktop Agent" not in custom_message
        assert "Data Agent" not in custom_message

def test_route_query_success():
    """Test successful routing of a query."""
    # Mock agent's run method to return a valid routing response
    test_response = [{
        "role": "assistant",
        "content": '{"agent": "search", "reason": "Web search needed", "reformulated_query": "test query", "confidence": "high"}'
    }]
    
    with patch("qwen_assistant.agents.base.Assistant") as mock_assistant:
        # Configure mock
        mock_instance = mock_assistant.return_value
        mock_instance.run.return_value = [test_response]
        
        # Create router agent
        agent = RouterAgent(llm_config={"model": "test-model"})
        
        # Test routing
        result = agent.route("test query")
        
        # Verify result
        assert result["agent"] == "search"
        assert "Web search needed" in result["reason"]
        assert result["reformulated_query"] == "test query"
        assert result["confidence"] == "high"

def test_route_query_json_in_markdown():
    """Test extracting JSON from markdown code blocks."""
    # Mock agent's run method to return JSON in markdown code block
    test_response = [{
        "role": "assistant",
        "content": '```json\n{"agent": "documentation", "reason": "API docs needed", "reformulated_query": "test query", "confidence": "medium"}\n```'
    }]
    
    with patch("qwen_assistant.agents.base.Assistant") as mock_assistant:
        # Configure mock
        mock_instance = mock_assistant.return_value
        mock_instance.run.return_value = [test_response]
        
        # Create router agent
        agent = RouterAgent(llm_config={"model": "test-model"})
        
        # Test routing
        result = agent.route("test query")
        
        # Verify result
        assert result["agent"] == "documentation"
        assert "API docs needed" in result["reason"]
        assert result["confidence"] == "medium"

def test_route_query_parse_error():
    """Test handling of JSON parsing errors."""
    # Mock agent's run method to return invalid JSON
    test_response = [{
        "role": "assistant",
        "content": 'Invalid JSON response'
    }]
    
    with patch("qwen_assistant.agents.base.Assistant") as mock_assistant:
        # Configure mock
        mock_instance = mock_assistant.return_value
        mock_instance.run.return_value = [test_response]
        
        # Create router agent
        agent = RouterAgent(llm_config={"model": "test-model"})
        
        # Test routing
        result = agent.route("test query")
        
        # Verify fallback behavior
        assert result["agent"] == "router"
        assert "Fallback" in result["reason"]
        assert result["reformulated_query"] == "test query"
        assert result["confidence"] == "low"

def test_route_query_invalid_agent():
    """Test handling of invalid agent in result."""
    # Mock response with nonexistent agent
    test_response = [{
        "role": "assistant",
        "content": '{"agent": "nonexistent", "reason": "Invalid agent", "reformulated_query": "test query", "confidence": "high"}'
    }]
    
    with patch("qwen_assistant.agents.base.Assistant") as mock_assistant:
        # Configure mock
        mock_instance = mock_assistant.return_value
        mock_instance.run.return_value = [test_response]
        
        # Create router agent
        agent = RouterAgent(llm_config={"model": "test-model"})
        
        # Test routing
        result = agent.route("test query")
        
        # Verify fallback behavior
        assert result["agent"] == "router"
        assert "Fallback" in result["reason"]
        assert result["confidence"] == "low"

def test_route_empty_query():
    """Test routing of an empty query."""
    with patch("qwen_assistant.agents.base.Assistant"):
        agent = RouterAgent(llm_config={"model": "test-model"})
        
        # Test routing
        result = agent.route("")
        
        # Verify result
        assert result["agent"] == "router"
        assert "Empty query" in result["reason"]
        assert result["confidence"] == "high"

def test_agent_registration():
    """Test agent registration and unregistration."""
    with patch("qwen_assistant.agents.base.Assistant"):
        agent = RouterAgent(llm_config={"model": "test-model"})
        
        # Initial state
        initial_agents = agent.get_available_agents()
        
        # Register new agent
        agent.register_agent("custom")
        assert "custom" in agent.available_agents
        
        # Try to register again (should have no effect)
        agent.register_agent("custom")
        assert len(agent.available_agents) == len(initial_agents) + 1
        
        # Unregister agent
        agent.unregister_agent("custom")
        assert "custom" not in agent.available_agents
        
        # Try to unregister router (should be prevented)
        agent.unregister_agent("router")
        assert "router" in agent.available_agents

def test_from_config():
    """Test creating router agent from configuration."""
    with patch("qwen_assistant.agents.base.Assistant"):
        config = {
            "name": "Test Router",
            "description": "Test router description",
            "llm": {"model": "test-model"},
            "mcp_servers": {"test-server": {"url": "test-url"}},
            "routing": {
                "available_agents": ["documentation", "search", "custom"],
                "system_message": "Custom system message"
            },
            "files": ["test.txt"]
        }
        
        agent = RouterAgent.from_config(config)
        
        # Assert instance created correctly
        assert agent.name == "Test Router"
        assert agent.description == "Test router description"
        assert agent.llm_config == {"model": "test-model"}
        assert agent.mcp_config == {"test-server": {"url": "test-url"}}
        assert agent.available_agents == {"documentation", "search", "custom"}