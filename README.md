# Qwen Multi-Assistant

An implementation of a Qwen3-based Agent-Army architecture that integrates multiple Model Context Protocol (MCP) servers. The system uses specialized sub-agents to handle different tool domains, coordinated by a central router agent.

## Overview

Qwen Multi-Assistant provides an intelligent agent system that can handle various tasks by routing user requests to specialized agents:

- **Router Agent**: Central orchestrator that analyzes user intent and selects appropriate specialized agents
- **Specialized Agents**:
  - **Data Agent (Airtable)**: Handles database operations and data management
  - **Desktop Agent (DesktopCommander)**: Manages file system and local machine operations
  - **Search Agent (Exa)**: Performs web search and information retrieval
  - **Documentation Agent (Context7)**: Manages documentation and knowledge access

## Architecture

The system follows a modular architecture with clear separation of concerns:

1. **Router Agent**: Central orchestrator that analyzes user intent, selects appropriate specialized agents, manages context transfer, and synthesizes responses.
2. **Specialized Agents**: Domain-specific agents that handle particular types of tasks.
3. **Context Management System**: Maintains conversation history, tracks entities, and manages task state across agent transitions.
4. **User Interface**: Provides a chat-based interaction using Gradio with file upload capabilities and tool usage visualization.

## Technical Stack

- **Backend**: Python 3.11+
- **LLM**: Qwen3 models (primarily Qwen3-235b for router, Qwen3-32b for agents)
- **UI Framework**: Gradio
- **Testing**: Pytest
- **MCP Servers**:
  - Airtable MCP Server
  - DesktopCommanderMCP
  - Exa MCP Server
  - Context7

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/qwen-assist-2.git
   cd qwen-assist-2
   ```

2. Set up your Python environment:
   ```bash
   # Make sure you have Poetry installed
   # Install dependencies
   poetry install
   ```

3. Configure your environment:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

## Usage

Start the application:

```bash
poetry run python -m qwen_assistant
```

The application will be available at http://localhost:7860 (default Gradio port).

## Development

This project is structured in phases:

1. **MVP Phase**: Basic router, core specialized agents, fundamental MCP integrations, and simple UI
2. **Enhancement Phase**: Advanced agent coordination, enhanced context management, and user experience improvements
3. **Scaling Phase**: Dynamic agent loading, performance optimization, and enterprise integration

## Contributing

1. Set up the development environment as described in the Installation section
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `poetry run pytest`
5. Submit a pull request

## License

[Insert appropriate license information here]