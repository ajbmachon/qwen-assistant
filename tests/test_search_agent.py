"""Tests for the Search Agent."""

import pytest
from unittest.mock import MagicMock, patch
from qwen_assistant.agents.search import SearchAgent

@pytest.fixture
def mock_assistant():
    """Create a mock Qwen-Agent Assistant."""
    assistant = MagicMock()
    assistant.run.return_value = iter([[{"role": "assistant", "content": "Mocked search response"}]])
    return assistant

@pytest.fixture
def search_agent(mock_assistant):
    """Create a SearchAgent with mocked Assistant."""
    with patch('qwen_assistant.agents.base.Assistant', return_value=mock_assistant):
        agent = SearchAgent(
            name="Test Search Agent",
            llm_config={"model": "test-model"},
            mcp_config={"exa": {"command": "test", "args": []}}
        )
        return agent

def test_search_agent_initialization():
    """Test SearchAgent initialization."""
    with patch('qwen_assistant.agents.base.Assistant') as mock_assistant_cls:
        # Configure the mock
        mock_instance = MagicMock()
        mock_assistant_cls.return_value = mock_instance
        
        agent = SearchAgent(
            name="Test Search Agent",
            llm_config={"model": "test-model"},
            mcp_config={"exa": {"command": "test", "args": []}}
        )
        
        assert agent.name == "Test Search Agent"
        assert agent.llm_config == {"model": "test-model"}
        assert agent.mcp_config == {"exa": {"command": "test", "args": []}}

def test_search_agent_missing_exa_config():
    """Test warning when Exa MCP is missing from config."""
    with patch('qwen_assistant.agents.base.Assistant'), \
         patch('qwen_assistant.agents.search.logger.warning') as mock_warning:
        agent = SearchAgent(
            name="Test Search Agent",
            mcp_config={"other_mcp": {"command": "test"}}
        )
        
        mock_warning.assert_called_once_with(
            "Exa MCP not found in configuration, SearchAgent may not function properly"
        )

def test_search_web(search_agent, mock_assistant):
    """Test search_web method."""
    for response in search_agent.search_web("test query"):
        assert response == [{"role": "assistant", "content": "Mocked search response"}]
    
    # Check that the assistant was called with the expected message
    mock_assistant.run.assert_called_once()
    # Get the arguments that run was called with
    kwargs = mock_assistant.run.call_args.kwargs
    # In newer versions, messages are passed as a kwarg
    assert 'messages' in kwargs
    messages = kwargs['messages']
    assert messages[0]["role"] == "user"
    assert "Search the web for: test query" in messages[0]["content"]

def test_search_research_papers(search_agent, mock_assistant):
    """Test search_research_papers method."""
    for response in search_agent.search_research_papers("quantum computing"):
        assert response == [{"role": "assistant", "content": "Mocked search response"}]
    
    # Check that the assistant was called with the expected message
    mock_assistant.run.assert_called_once()
    # Get the arguments that run was called with
    kwargs = mock_assistant.run.call_args.kwargs
    # In newer versions, messages are passed as a kwarg
    assert 'messages' in kwargs
    messages = kwargs['messages']
    assert messages[0]["role"] == "user"
    assert "Find research papers about: quantum computing" in messages[0]["content"]

def test_extract_content(search_agent, mock_assistant):
    """Test extract_content method."""
    for response in search_agent.extract_content("https://example.com"):
        assert response == [{"role": "assistant", "content": "Mocked search response"}]
    
    # Check that the assistant was called with the expected message
    mock_assistant.run.assert_called_once()
    # Get the arguments that run was called with
    kwargs = mock_assistant.run.call_args.kwargs
    # In newer versions, messages are passed as a kwarg
    assert 'messages' in kwargs
    messages = kwargs['messages']
    assert messages[0]["role"] == "user"
    assert "Extract the content from this URL: https://example.com" in messages[0]["content"]

def test_is_search_query():
    """Test is_search_query method."""
    with patch('qwen_assistant.agents.base.Assistant'):
        agent = SearchAgent()
        
        # True cases
        assert agent.is_search_query("search for quantum computing") == True
        assert agent.is_search_query("find information about climate change") == True
        assert agent.is_search_query("what is the latest news on AI") == True
        
        # False cases
        assert agent.is_search_query("tell me a joke") == False
        assert agent.is_search_query("create a new file") == False
        assert agent.is_search_query("hello") == False

def test_from_config():
    """Test from_config class method."""
    with patch('qwen_assistant.agents.base.Assistant') as mock_assistant_cls:
        # Configure the mock to have a system_message attribute
        mock_instance = MagicMock()
        mock_instance.system_message = "Default message"
        mock_assistant_cls.return_value = mock_instance
        
        config = {
            "name": "Config Search Agent",
            "description": "Custom description",
            "llm": {"model": "config-model"},
            "mcp_servers": {"exa": {"command": "config-test"}},
            "search": {
                "system_message": "Custom system message"
            }
        }
        
        agent = SearchAgent.from_config(config)
        
        assert agent.name == "Config Search Agent"
        assert agent.description == "Custom description"
        assert agent.llm_config == {"model": "config-model"}
        assert agent.mcp_config == {"exa": {"command": "config-test"}}