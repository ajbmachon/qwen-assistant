"""Tests for the documentation agent."""

from unittest.mock import patch
from qwen_assistant.agents.documentation import DocumentationAgent

def test_documentation_agent_init():
    """Test initialization of the documentation agent."""
    with patch("qwen_assistant.agents.base.Assistant") as mock_assistant:
        # Create documentation agent with minimal config
        agent = DocumentationAgent(
            llm_config={"model": "test-model"},
            mcp_config={"context7": {"command": "mock-command"}}
        )
        
        # Assert instance created correctly
        assert agent.name == "Documentation Agent"
        assert "libraries, APIs, and technical documentation" in agent.description
        assert mock_assistant.called
        assert len(agent.supported_libraries) == 0

def test_documentation_agent_with_supported_libraries():
    """Test initialization with supported libraries."""
    with patch("qwen_assistant.agents.base.Assistant"):
        # Create documentation agent with supported libraries
        supported_libs = {"python", "javascript", "react"}
        agent = DocumentationAgent(
            llm_config={"model": "test-model"},
            mcp_config={"context7": {"command": "mock-command"}},
            supported_libraries=supported_libs
        )
        
        # Assert instance created correctly
        assert agent.supported_libraries == supported_libs

def test_documentation_agent_warning_no_context7():
    """Test warning when Context7 MCP not provided."""
    with patch("qwen_assistant.agents.base.Assistant"), \
         patch("qwen_assistant.agents.documentation.logger") as mock_logger:
        # Create documentation agent without Context7 MCP
        DocumentationAgent(
            llm_config={"model": "test-model"},
            mcp_config={"other_mcp": {"command": "mock-command"}}
        )
        
        # Assert warning logged
        mock_logger.warning.assert_called_once()
        assert "Context7 MCP not found" in mock_logger.warning.call_args[0][0]

def test_is_documentation_query():
    """Test detection of documentation queries."""
    with patch("qwen_assistant.agents.base.Assistant"):
        agent = DocumentationAgent(
            llm_config={"model": "test-model"},
            mcp_config={"context7": {"command": "mock-command"}}
        )
        
        # Test with documentation queries
        assert agent.is_documentation_query("What's the documentation for React?")
        assert agent.is_documentation_query("How do I use the pandas library?")
        assert agent.is_documentation_query("Show me the API reference for TensorFlow.")
        
        # Test with non-documentation queries
        assert not agent.is_documentation_query("What's the weather today?")
        assert not agent.is_documentation_query("Tell me a joke.")
        assert not agent.is_documentation_query("How old is the Eiffel Tower?")

def test_resolve_library():
    """Test resolving a library name to a Context7 ID."""
    with patch("qwen_assistant.agents.base.Assistant") as mock_assistant:
        # Setup mock response
        mock_instance = mock_assistant.return_value
        mock_instance.run.return_value = [[{"role": "assistant", "content": "context7/react-id"}]]
        
        # Create documentation agent
        agent = DocumentationAgent(
            llm_config={"model": "test-model"},
            mcp_config={"context7": {"command": "mock-command"}}
        )
        
        # Test library resolution
        result = agent.resolve_library("react")
        
        # Verify result
        assert mock_instance.run.called
        assert result == "context7/react-id"

def test_get_documentation():
    """Test getting documentation for a library."""
    with patch("qwen_assistant.agents.base.Assistant") as mock_assistant:
        # Setup mock response
        mock_instance = mock_assistant.return_value
        mock_doc_content = "React is a JavaScript library for building user interfaces."
        mock_instance.run.return_value = [[{"role": "assistant", "content": mock_doc_content}]]
        
        # Create documentation agent
        agent = DocumentationAgent(
            llm_config={"model": "test-model"},
            mcp_config={"context7": {"command": "mock-command"}}
        )
        
        # Test getting documentation
        result = agent.get_documentation("context7/react-id")
        
        # Verify result
        assert mock_instance.run.called
        assert result == mock_doc_content

def test_get_documentation_with_topic():
    """Test getting documentation for a specific topic."""
    with patch("qwen_assistant.agents.base.Assistant") as mock_assistant:
        # Setup mock response
        mock_instance = mock_assistant.return_value
        mock_doc_content = "React Hooks documentation..."
        mock_instance.run.return_value = [[{"role": "assistant", "content": mock_doc_content}]]
        
        # Create documentation agent
        agent = DocumentationAgent(
            llm_config={"model": "test-model"},
            mcp_config={"context7": {"command": "mock-command"}}
        )
        
        # Test getting documentation with topic
        result = agent.get_documentation("context7/react-id", topic="hooks")
        
        # Verify result
        assert mock_instance.run.called
        # Check if topic is mentioned in the user message
        called_messages = mock_instance.run.call_args[1]["messages"]
        assert "topic: hooks" in called_messages[0]["content"]
        assert result == mock_doc_content

def test_from_config():
    """Test creating documentation agent from configuration."""
    with patch("qwen_assistant.agents.base.Assistant"):
        config = {
            "name": "Test Documentation Agent",
            "description": "Test description",
            "llm": {"model": "test-model"},
            "mcp_servers": {"context7": {"command": "test-command"}},
            "documentation": {
                "system_message": "Custom system message",
                "supported_libraries": ["python", "javascript"]
            },
            "files": ["test.txt"]
        }
        
        agent = DocumentationAgent.from_config(config)
        
        # Assert instance created correctly
        assert agent.name == "Test Documentation Agent"
        assert agent.description == "Test description"
        assert agent.llm_config == {"model": "test-model"}
        assert agent.mcp_config == {"context7": {"command": "test-command"}}
        assert agent.supported_libraries == {"python", "javascript"}