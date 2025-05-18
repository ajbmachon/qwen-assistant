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
python src/main.py
```

## Project Structure

```
qwen-assist-2/
├── src/                    # Source code
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