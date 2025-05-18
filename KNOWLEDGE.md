# Knowledge Repository Summary

This document provides a summary of key knowledge items in the Qwen Multi-Assistant project.

## Architecture and System Design

### System Architecture (know_443e40c02580465195a25800f19e9397)
The Qwen Multi-Assistant system follows a modular architecture with a Router Agent as central orchestrator, specialized agents for different domains, a context management system, and a Gradio-based UI. The architecture emphasizes loose coupling, single responsibility, extensibility, and progressive enhancement.

### Qwen3 Agent-Army Overview (know_0ef69ff3259a432583915840d612c667)
The system implements an Agent-Army pattern with a Router Agent built on Qwen3-235b, specialized sub-agents for different domains, an MCP Server integration layer, and cross-agent context management. Technical requirements include Python 3.10+, Qwen3 model access, and various MCP server dependencies.

## Agent Implementations

### Router Agent (know_6a4929a4129d4932a015b6e05784d018)
The Router Agent analyzes user queries and directs them to appropriate specialized agents. Key features include dynamic agent registration, customizable system messages, robust JSON parsing, validation with fallbacks, and confidence levels for routing decisions.

### Documentation Agent (know_d29679e9cc124d9b9cc399ff7abd19c8)
The Documentation Agent handles library and API documentation queries using the Context7 MCP server. Core capabilities include library resolution, documentation retrieval, and query detection. Implementation resides in `qwen_assistant/agents/documentation.py`.

### Search Agent (know_3d1446d351a243b59e43771bdefd7ac7)
The Search Agent handles web search operations using the Exa MCP server, providing methods for web search, research paper search, Twitter search, company research, content extraction, competitor finding, and LinkedIn search.

### Data Agent (know_2e3da237f38e47f59691f06d454b9802)
The Data Agent handles structured data operations using the Airtable MCP server. It provides functionality for querying, creating, updating, and deleting records in Airtable bases.

## Design Guidelines

### Router Agent Design (know_5acdf56e0d74416da163dbd41c607729)
The Router Agent should focus on intent classification, agent selection, context management, response synthesis, and error handling. Implementation recommendations include using the largest available model and creating metrics to track selection accuracy.

### Specialized Agents Design (know_cc0f4fb134b641649ac386644a68d47a)
Each specialized agent should focus on a specific domain area, leverage appropriate MCP tools, maintain consistent interfaces, handle domain-specific errors, and format responses appropriately.

### Context Management (know_de2cdbcc747c460c8c646beaac1c1a06)
The context management system should maintain conversation history, track entities, manage task state, and provide relevant context to specialized agents. Implementation should include a central context store with clear interfaces.

### User Interface (know_910a15c2100f4bc58c1c1be8fa085099)
The UI should focus on simplicity, transparency, responsiveness, and accessibility. Key components include a chat interface, agent visibility indicators, tool usage visualization, and error presentation.

## Implementation Details

### Project Infrastructure (know_8e2b0fc34fb044999d8d846657ed1b13)
The project has a structured directory organization, key components including a Base Agent, Router Agent, configuration system, Gradio UI, and testing framework. Dependencies include qwen-agent, python-dotenv, pyyaml, and gradio.

### MCP Server Integration (know_836b1063a519495b9b7c762594b4cf2a)
Details of the four MCP servers: Airtable MCP Server for database operations, DesktopCommanderMCP for system interaction, Exa MCP Server for search operations, and Context7 for documentation management. The integration strategy covers authentication, standardized interfaces, and tool discovery.

### Model Configuration (know_b396aff2213d4f0fb6024c92a45bb348)
Qwen3 model selection includes Qwen3-235b for the Router Agent and Qwen3-32b for specialized agents, using OpenRouter as the model server. Configuration parameters include temperature, top_p, max_tokens, and timeout settings customized per agent role.

## Best Practices

### Project Structure (know_925ed6474580497186a183098048adb8)
The project follows a modular structure with clear separation of concerns. Key modules include configuration management, agent modules, context management, MCP integration, user interface, and utilities.

### Error Handling (know_b60a3abd64a14c368e890292ea2c5c5d)
The error handling strategy emphasizes graceful degradation, user transparency, detailed logging, and recovery mechanisms. Error categories include connection errors, authentication errors, tool execution errors, model generation errors, and context management errors.

### Security Considerations (know_3bb6ee5de7164b0e8de17d9d0da1f64b)
Security best practices include proper API key management, data protection measures, access control if implementing user accounts, and MCP server security considerations.

### Testing Strategy (know_fa5cad5bcaca4a51b2b3bd1d25c11552)
Testing leverages pytest as the primary framework with unit testing for individual components, integration testing for component interactions, and system testing for end-to-end workflows. Special considerations include mock responses for LLM API calls and test fixtures for MCP server responses.

## Development Phases

### MVP Phase (covered in multiple knowledge items)
Focuses on basic router implementation, core specialized agents, fundamental MCP integrations, and a simple UI with minimal context sharing.

### Enhancement Phase (know_2bfaba7abc8b4d80bfe38200731d82b9)
Focuses on advanced agent coordination, enhanced context management, user experience improvements, and extended workflows that span multiple agents.

### Scaling Phase (know_e9854de7f8e44f9da41999c13c4d655c)
Addresses scalable agent management, advanced routing intelligence, performance optimization, and enterprise integration with authentication and permission management.