# Qwen-Assist-2

Multi-agent system built on the Qwen3 LLM using the Qwen-Agent framework. This project implements a modular agent-army architecture for distributed task execution.

## Features

- Router Agent for task delegation
- Specialized agents for different domains:
  - Documentation Agent (Context7)
  - Search Agent (Exa MCP)
  - Desktop Agent (DesktopCommanderMCP)
  - Data Agent (Airtable MCP)
- Gradio-based UI for interaction
- Context sharing between agents

### Data Agent

The Data Agent provides structured data operations via Airtable MCP, allowing users to:

- List and navigate Airtable bases, tables, and fields
- Query data with customizable filters and limits
- Create, update, and delete records
- Analyze data with AI-powered insights

Example usage:
```python
from qwen_assistant.agents.data import DataAgent

# Initialize with MCP config
data_agent = DataAgent(mcp_config={"airtable": {...}})

# Query records
for response in data_agent.query_records(
    base_id="appXXXXXXXXXXXXXX",
    table_id="tblYYYYYYYYYYYYYY",
    filter_formula="AND({Status}='Active')",
    max_records=10
):
    # Process response
    print(response)
```

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/qwen-assist-2.git
cd qwen-assist-2

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Create a `.env` file in the project root with your API keys
2. Configure the MCP servers in `config.yaml`

### Running the Application

```bash
python -m qwen_assistant.main
```

## Project Structure

```
qwen-assist-2/
├── qwen_assistant/         # Source code
│   ├── agents/             # Agent implementations
│   │   ├── router.py       # Router agent
│   │   ├── documentation.py # Documentation agent
│   │   ├── search.py       # Search agent
│   │   ├── desktop.py      # Desktop agent
│   │   └── data.py         # Data agent
│   ├── ui/                 # UI components
│   ├── utils/              # Utility functions
│   └── main.py             # Entry point
├── tests/                  # Test suite
├── config/                 # Configuration files
├── README.md               # Project documentation
└── requirements.txt        # Dependencies
```

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project uses ruff for linting and mypy for type checking.

```bash
ruff check .
mypy .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.