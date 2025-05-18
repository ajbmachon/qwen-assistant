"""Tests for the router agent."""

import pytest
from unittest.mock import patch, MagicMock
from src.agents.router import RouterAgent

def test_router_agent_init():
    """Test initialization of the router agent."""
    with patch("src.agents.base.Assistant") as mock_assistant:
        # Create router agent with minimal config
        agent = RouterAgent(
            llm_config={"model": "test-model"},
            mcp_config={}
        )
        
        # Assert instance created correctly
        assert agent.name == "Router Agent"
        assert "Routes queries" in agent.description
        assert mock_assistant.called

def test_route_query_success():
    """Test successful routing of a query."""
    # Mock agent's run method to return a valid routing response
    test_response = [{
        "role": "assistant",
        "content": '{"agent": "search", "reason": "Web search needed", "reformulated_query": "test query"}'
    }]
    
    with patch("src.agents.base.Assistant") as mock_assistant:
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

def test_route_query_json_in_markdown():
    """Test extracting JSON from markdown code blocks."""
    # Mock agent's run method to return JSON in markdown code block
    test_response = [{
        "role": "assistant",
        "content": '```json\n{"agent": "documentation", "reason": "API docs needed", "reformulated_query": "test query"}\n```'
    }]
    
    with patch("src.agents.base.Assistant") as mock_assistant:
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

def test_route_query_parse_error():
    """Test handling of JSON parsing errors."""
    # Mock agent's run method to return invalid JSON
    test_response = [{
        "role": "assistant",
        "content": 'Invalid JSON response'
    }]
    
    with patch("src.agents.base.Assistant") as mock_assistant:
        # Configure mock
        mock_instance = mock_assistant.return_value
        mock_instance.run.return_value = [test_response]
        
        # Create router agent
        agent = RouterAgent(llm_config={"model": "test-model"})
        
        # Test routing
        result = agent.route("test query")
        
        # Verify fallback behavior
        assert result["agent"] == "router"
        assert "Failed to parse" in result["reason"]
        assert result["reformulated_query"] == "test query"