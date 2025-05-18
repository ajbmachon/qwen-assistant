# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Qwen-Assist-2 is a multi-agent system built on the Qwen3 LLM using the Qwen-Agent framework. It implements a modular agent-army architecture for distributed task execution with specialized agents for different domains:

- Router Agent: Central coordinator for task delegation
- Documentation Agent: Uses Context7 for library and API documentation
- Search Agent: Uses Exa for web searches and knowledge retrieval
- Desktop Agent: Handles file system and local command operations
- Data Agent: Interacts with Airtable for structured data operations

## Development Environment

### Setup and Installation

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies using Poetry (recommended)
poetry install

# Alternatively, use pip
pip install -r requirements.txt
```

### Configuration

1. Create a `.env` file in the project root with your API keys:
   ```
   DASHSCOPE_API_KEY=your_dashscope_key
   EXA_API_KEY=your_exa_key
   AIRTABLE_API_KEY=your_airtable_key
   ```

2. The application uses config files in the `config/` directory. By default, it will use `config/config.yaml` or fall back to `config/default_config.yaml`.

### Common Commands

```bash
# Run the application in CLI mode
poetry run python -m qwen_assistant.main

# Run the application with Gradio web UI
poetry run python -m qwen_assistant.main --gui

# Run with a specific config file
poetry run python -m qwen_assistant.main --config path/to/config.yaml

# Run in debug mode
poetry run python -m qwen_assistant.main --debug

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=qwen_assistant

# Run tests for a specific module
poetry run pytest tests/test_router.py

# Run linting
poetry run ruff check .

# Run type checking
poetry run mypy .
```

## Code Architecture

### Core Components

1. **Router Agent (`qwen_assistant/agents/router.py`)**: 
   - Central decision-making component that analyzes user queries
   - Routes requests to specialized agents based on intent analysis
   - Manages available agents and their capabilities

2. **Base Agent (`qwen_assistant/agents/base.py`)**:
   - Abstract base class for all agents in the system
   - Handles LLM configuration and interaction via Qwen-Agent
   - Provides common functionality for all specialized agents

3. **User Interfaces**:
   - Command-line interface in `main.py`
   - Gradio web interface in `ui/gradio_interface.py`

4. **Configuration System**:
   - YAML-based configuration with environment variable support
   - Handles LLM settings, MCP server configuration, and app settings

### Data Flow

1. User input is received via CLI or Gradio UI
2. Router agent analyzes the query and determines the best specialized agent
3. Request is forwarded to the appropriate agent via the Qwen-Agent framework
4. Agent processes the request using its MCP tools (Context7, Exa, etc.)
5. Response is returned to the user

## Testing Guidelines

- Tests are written using pytest and located in the `tests/` directory
- Mock LLM responses and MCP servers during testing
- Ensure test coverage for router logic, configuration parsing, and agent communication

## Development Workflow

1. Use feature branches for new functionality
2. Write tests for new features
3. Run linting and type checking before committing
4. Follow existing code style and documentation patterns
5. Update configuration files for any new MCP services or settings

## Task Management

When working with the project, always:

1. Follow the task planning and implementation approach described in the task instructions
2. Document decisions and technical patterns using knowledge items
3. Break complex tasks into manageable subtasks when necessary
4. Maintain proper dependencies between related tasks
5. Update task status appropriately throughout the development cycle