# Tableau MCP Server

A Model Context Protocol (MCP) server that enables AI agents to generate Tableau workbooks programmatically.

## What is this MCP?

This MCP server provides AI agents with the ability to:
- Generate complete Tableau workbook (.twb) files
- Create visualizations (bar charts, line charts, scatter plots, etc.)
- Configure data connections and worksheets
- Apply filters, sorting, and formatting
- Build dashboards with multiple visualizations

## How to use

### Installation

```bash
pip install tableau-mcp-kartik
```

### MCP Server Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "tableau-mcp": {
      "command": "python",
      "args": ["-m", "tableau_mcp"],
      "env": {}
    }
  }
}
```

### Available Tools

- `generate_tableau_workbook`: Create complete Tableau workbooks with visualizations
- `profile_data_schema`: Analyze CSV data structure for optimal visualization recommendations
- `get_sample_datasets`: Access built-in sample datasets for testing

### Basic Usage

Once connected, you can ask your AI agent to:
- "Create a bar chart showing sales by region using my CSV data"
- "Generate a dashboard with multiple visualizations"
- "Build a time series chart with filtering capabilities"

The MCP will generate ready-to-use Tableau workbook files that can be opened directly in Tableau Desktop or published to Tableau Server.

## Requirements

- Python 3.8+
- Compatible with any MCP client (Claude Desktop, etc.)
- Generated workbooks work with Tableau Desktop 2020.1+