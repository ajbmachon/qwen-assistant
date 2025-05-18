"""Data agent for Qwen-Assist-2.

This agent is responsible for handling data operations using the Airtable MCP server.
"""

import logging
from typing import Dict, Any, List, Optional, Iterator, Union
from .base import BaseAgent
from qwen_agent.llm.schema import Message

logger = logging.getLogger(__name__)

DATA_AGENT_SYSTEM_MESSAGE = """You are a Data Agent with access to Airtable MCP for structured data operations.

You can perform the following operations:
1. List bases, tables, and fields
2. Query records from tables
3. Create new records in tables
4. Update existing records
5. Delete records
6. Perform data analysis on records

When accessing Airtable:
- Always verify the base, table, and field identifiers before operations
- Format data appropriately for creation and updates
- Handle errors gracefully with informative messages
- Provide clear summaries of operation results

For data analysis tasks:
- Offer insights based on patterns in the data
- Calculate relevant statistics when appropriate
- Format results in a readable way
- Suggest visualizations when they would be helpful

When the user asks about data, always think step by step about:
1. Which base and table they need
2. What operation they want to perform
3. Any conditions or filters to apply
4. How to best present the results
"""

class DataAgent(BaseAgent):
    """Data agent responsible for handling structured data operations via Airtable MCP."""
    
    def __init__(
        self,
        name: str = "Data Agent",
        description: str = "Handles structured data operations using Airtable",
        llm_config: Optional[Dict[str, Any]] = None,
        mcp_config: Optional[Dict[str, Any]] = None,
        system_message: str = DATA_AGENT_SYSTEM_MESSAGE,
        files: Optional[List[str]] = None
    ):
        """Initialize the data agent.
        
        Args:
            name: Agent name.
            description: Short description of the agent.
            llm_config: Configuration for the LLM.
            mcp_config: Configuration for MCP servers, specifically Airtable MCP.
            system_message: System message for the agent. Defaults to DATA_AGENT_SYSTEM_MESSAGE.
            files: List of files to provide to the agent.
        """
        # Extract Airtable-specific MCP config if full MCP config dict is provided
        if mcp_config and "airtable" in mcp_config:
            airtable_config = {"airtable": mcp_config["airtable"]}
        else:
            airtable_config = mcp_config or {}
        
        super().__init__(
            name=name,
            description=description,
            llm_config=llm_config or {},
            mcp_config=airtable_config,
            system_message=system_message,
            files=files or []
        )
        
        logger.info("Data Agent initialized")
    
    def process(
        self, 
        query: str, 
        history: Optional[List[Message]] = None
    ) -> Iterator[List[Message]]:
        """Process a data-related query.
        
        Args:
            query: User query to process.
            history: Optional conversation history.
            
        Returns:
            Iterator of response messages.
        """
        messages = history or []
        messages.append({"role": "user", "content": query})
        
        logger.info(f"Processing data query: {query[:50]}...")
        return self.run(messages=messages)
    
    def list_bases(self) -> Iterator[List[Message]]:
        """List available Airtable bases.
        
        Returns:
            Iterator of response messages with base information.
        """
        return self.process("List all available Airtable bases")
    
    def list_tables(self, base_id: str) -> Iterator[List[Message]]:
        """List tables in a specific base.
        
        Args:
            base_id: The ID of the Airtable base.
            
        Returns:
            Iterator of response messages with table information.
        """
        return self.process(f"List all tables in Airtable base with ID {base_id}")
    
    def list_fields(self, base_id: str, table_id: str) -> Iterator[List[Message]]:
        """List fields in a specific table.
        
        Args:
            base_id: The ID of the Airtable base.
            table_id: The ID of the table.
            
        Returns:
            Iterator of response messages with field information.
        """
        return self.process(f"List all fields in table {table_id} of Airtable base {base_id}")
    
    def query_records(
        self, 
        base_id: str, 
        table_id: str, 
        filter_formula: Optional[str] = None,
        max_records: Optional[int] = None
    ) -> Iterator[List[Message]]:
        """Query records from a table.
        
        Args:
            base_id: The ID of the Airtable base.
            table_id: The ID of the table.
            filter_formula: Optional Airtable formula for filtering records.
            max_records: Optional maximum number of records to return.
            
        Returns:
            Iterator of response messages with query results.
        """
        query = f"Query records from table {table_id} in Airtable base {base_id}"
        if filter_formula:
            query += f" with filter formula: {filter_formula}"
        if max_records:
            query += f" limited to {max_records} records"
        
        return self.process(query)
    
    def create_record(
        self, 
        base_id: str, 
        table_id: str, 
        fields: Dict[str, Any]
    ) -> Iterator[List[Message]]:
        """Create a new record in a table.
        
        Args:
            base_id: The ID of the Airtable base.
            table_id: The ID of the table.
            fields: Dictionary of field names and values for the new record.
            
        Returns:
            Iterator of response messages with creation result.
        """
        fields_str = ", ".join([f"{key}: {value}" for key, value in fields.items()])
        query = f"Create a new record in table {table_id} of Airtable base {base_id} with fields: {fields_str}"
        
        return self.process(query)
    
    def update_record(
        self, 
        base_id: str, 
        table_id: str, 
        record_id: str,
        fields: Dict[str, Any]
    ) -> Iterator[List[Message]]:
        """Update an existing record in a table.
        
        Args:
            base_id: The ID of the Airtable base.
            table_id: The ID of the table.
            record_id: The ID of the record to update.
            fields: Dictionary of field names and values to update.
            
        Returns:
            Iterator of response messages with update result.
        """
        fields_str = ", ".join([f"{key}: {value}" for key, value in fields.items()])
        query = f"Update record {record_id} in table {table_id} of Airtable base {base_id} with fields: {fields_str}"
        
        return self.process(query)
    
    def delete_record(
        self, 
        base_id: str, 
        table_id: str, 
        record_id: str
    ) -> Iterator[List[Message]]:
        """Delete a record from a table.
        
        Args:
            base_id: The ID of the Airtable base.
            table_id: The ID of the table.
            record_id: The ID of the record to delete.
            
        Returns:
            Iterator of response messages with deletion result.
        """
        query = f"Delete record {record_id} from table {table_id} in Airtable base {base_id}"
        
        return self.process(query)