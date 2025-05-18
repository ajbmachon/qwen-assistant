"""Tests for the Data Agent."""

import pytest
from unittest.mock import patch, MagicMock
from qwen_assistant.agents.data import DataAgent
from qwen_agent.llm.schema import Message

# Mock the Qwen-Agent imports to avoid actual model initialization
@pytest.fixture(autouse=True)
def mock_qwen_agent():
    """Mock the Qwen-Agent Assistant class."""
    with patch('qwen_assistant.agents.base.Assistant') as mock_assistant:
        # Configure the mock assistant's run method to return a simple response
        mock_instance = MagicMock()
        mock_instance.run.return_value = iter([[{"role": "assistant", "content": "Mocked response"}]])
        mock_assistant.return_value = mock_instance
        yield mock_assistant

@pytest.fixture
def data_agent():
    """Create a test data agent with mocked config."""
    llm_config = {"model": "qwen-max", "model_server": "openrouter", "api_key": "mock-key"}
    mcp_config = {
        "airtable": {
            "command": "mock-command",
            "args": ["--api-key", "mock-key"]
        }
    }
    return DataAgent(
        llm_config=llm_config, 
        mcp_config=mcp_config
    )

def test_data_agent_init(data_agent):
    """Test data agent initialization."""
    assert data_agent.name == "Data Agent"
    assert "Handles structured data operations" in data_agent.description
    assert "airtable" in data_agent.mcp_config

def test_data_agent_mcp_extraction(mock_qwen_agent):
    """Test that Airtable config is extracted from full MCP config."""
    full_mcp_config = {
        "airtable": {"command": "npx", "args": ["mock"]},
        "other_mcp": {"command": "other"}
    }
    
    llm_config = {"model": "qwen-max", "model_server": "openrouter", "api_key": "mock-key"}
    agent = DataAgent(llm_config=llm_config, mcp_config=full_mcp_config)
    assert "airtable" in agent.mcp_config
    assert "other_mcp" not in agent.mcp_config

@patch.object(DataAgent, 'run')
def test_process_query(mock_run, data_agent):
    """Test processing a simple query."""
    mock_response = [{"role": "assistant", "content": "Test response"}]
    mock_run.return_value = iter([mock_response])
    
    query = "List all bases"
    history = [{"role": "user", "content": "Previous message"}]
    
    responses = list(data_agent.process(query, history))
    
    # Check that run was called with messages
    mock_run.assert_called_once()
    call_args = mock_run.call_args[1]
    assert "messages" in call_args
    
    # The history is modified in-place in process() so we can't directly compare
    # Instead check that run() was called with both the original message and the new query
    called_messages = call_args["messages"]
    assert any(msg["content"] == "Previous message" for msg in called_messages if msg["role"] == "user")
    assert any(msg["content"] == "List all bases" for msg in called_messages if msg["role"] == "user")
    
    # Check that the response is returned correctly
    assert responses == [mock_response]

@patch.object(DataAgent, 'process')
def test_list_bases(mock_process, data_agent):
    """Test list_bases method."""
    mock_response = [{"role": "assistant", "content": "Base list"}]
    mock_process.return_value = iter([mock_response])
    
    responses = list(data_agent.list_bases())
    
    mock_process.assert_called_once_with("List all available Airtable bases")
    assert responses == [mock_response]

@patch.object(DataAgent, 'process')
def test_list_tables(mock_process, data_agent):
    """Test list_tables method."""
    mock_response = [{"role": "assistant", "content": "Table list"}]
    mock_process.return_value = iter([mock_response])
    
    base_id = "appXXXXXXXXXXXXXX"
    responses = list(data_agent.list_tables(base_id))
    
    mock_process.assert_called_once()
    call_args = mock_process.call_args[0]
    assert base_id in call_args[0]
    assert responses == [mock_response]

@patch.object(DataAgent, 'process')
def test_query_records(mock_process, data_agent):
    """Test query_records method with filter and limit."""
    mock_response = [{"role": "assistant", "content": "Query results"}]
    mock_process.return_value = iter([mock_response])
    
    base_id = "appXXXXXXXXXXXXXX"
    table_id = "tblYYYYYYYYYYYYYY"
    filter_formula = "AND(field='value')"
    max_records = 10
    
    responses = list(data_agent.query_records(
        base_id=base_id,
        table_id=table_id,
        filter_formula=filter_formula,
        max_records=max_records
    ))
    
    mock_process.assert_called_once()
    call_args = mock_process.call_args[0]
    assert base_id in call_args[0]
    assert table_id in call_args[0]
    assert filter_formula in call_args[0]
    assert str(max_records) in call_args[0]
    assert responses == [mock_response]

@patch.object(DataAgent, 'process')
def test_create_record(mock_process, data_agent):
    """Test create_record method."""
    mock_response = [{"role": "assistant", "content": "Record created"}]
    mock_process.return_value = iter([mock_response])
    
    base_id = "appXXXXXXXXXXXXXX"
    table_id = "tblYYYYYYYYYYYYYY"
    fields = {"Name": "Test", "Value": 123}
    
    responses = list(data_agent.create_record(
        base_id=base_id,
        table_id=table_id,
        fields=fields
    ))
    
    mock_process.assert_called_once()
    call_args = mock_process.call_args[0]
    assert base_id in call_args[0]
    assert table_id in call_args[0]
    assert "Name: Test" in call_args[0]
    assert "Value: 123" in call_args[0]
    assert responses == [mock_response]

@patch.object(DataAgent, 'process')
def test_update_record(mock_process, data_agent):
    """Test update_record method."""
    mock_response = [{"role": "assistant", "content": "Record updated"}]
    mock_process.return_value = iter([mock_response])
    
    base_id = "appXXXXXXXXXXXXXX"
    table_id = "tblYYYYYYYYYYYYYY"
    record_id = "recZZZZZZZZZZZZZZ"
    fields = {"Status": "Complete"}
    
    responses = list(data_agent.update_record(
        base_id=base_id,
        table_id=table_id,
        record_id=record_id,
        fields=fields
    ))
    
    mock_process.assert_called_once()
    call_args = mock_process.call_args[0]
    assert base_id in call_args[0]
    assert table_id in call_args[0]
    assert record_id in call_args[0]
    assert "Status: Complete" in call_args[0]
    assert responses == [mock_response]

@patch.object(DataAgent, 'process')
def test_delete_record(mock_process, data_agent):
    """Test delete_record method."""
    mock_response = [{"role": "assistant", "content": "Record deleted"}]
    mock_process.return_value = iter([mock_response])
    
    base_id = "appXXXXXXXXXXXXXX"
    table_id = "tblYYYYYYYYYYYYYY"
    record_id = "recZZZZZZZZZZZZZZ"
    
    responses = list(data_agent.delete_record(
        base_id=base_id,
        table_id=table_id,
        record_id=record_id
    ))
    
    mock_process.assert_called_once()
    call_args = mock_process.call_args[0]
    assert base_id in call_args[0]
    assert table_id in call_args[0]
    assert record_id in call_args[0]
    assert "Delete record" in call_args[0]
    assert responses == [mock_response]