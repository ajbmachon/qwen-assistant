# Qwen Multi-Assistant Agents

This directory contains the specialized agents for the Qwen Multi-Assistant system.

## Agent Structure

- `base.py`: Base agent class that all specialized agents inherit from
- `desktop.py`: Desktop Agent for file system and local machine operations
- (Other agents like data.py, search.py, documentation.py)

## Desktop Agent

The Desktop Agent is responsible for handling file system and local machine operations using the DesktopCommanderMCP server.

### Capabilities

- Execute terminal commands
- Read and write files
- Search for files and code
- List directories and files
- Get file metadata

### Configuration

Configure the Desktop Agent in `.env` or the configuration file:

```yaml
agents:
  desktop:
    enabled: true
    mcp_endpoint: "http://localhost:9000"
```

Or through environment variables:

```
QWEN_MCP_DESKTOP_ENDPOINT=http://localhost:9000
```

### Usage

The Desktop Agent can be used to:

1. Execute shell commands:
   ```python
   response = await desktop_agent.execute_command("ls -la")
   ```

2. Read files:
   ```python
   response = await desktop_agent.read_file("/path/to/file.txt")
   ```

3. Write files:
   ```python
   response = await desktop_agent.write_file("/path/to/file.txt", "Content")
   ```

4. Search for files:
   ```python
   response = await desktop_agent.search_files("/path/to/dir", "*.py")
   ```

5. Search code:
   ```python
   response = await desktop_agent.search_code("/path/to/dir", "def main")
   ```

### Integration with DesktopCommanderMCP

The Desktop Agent requires the DesktopCommanderMCP server to be running. Follow these steps to set it up:

1. Install DesktopCommanderMCP:
   ```bash
   npx @wonderwhy-er/desktop-commander-mcp
   ```

2. Configure the endpoint in your Qwen Multi-Assistant configuration.

3. Ensure the Desktop Agent is enabled in your configuration.