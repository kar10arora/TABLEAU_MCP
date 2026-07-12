# Tableau MCP Server

A Model Context Protocol (MCP) server that enables AI agents to generate Tableau workbooks programmatically.

> **Installation Note**: This package is distributed with an automated installer. Download the distribution package from GitHub and run the included `install.bat` script for easy setup.

## What is this MCP?

This MCP server provides AI agents with the ability to:
- Generate complete Tableau workbook (.twb) files
- Create visualizations (bar charts, line charts, scatter plots, etc.)
- Configure data connections and worksheets
- Apply filters, sorting, and formatting
- Build dashboards with multiple visualizations

## How to use

### Installation

1. Download the distribution package from the GitHub repository
2. Extract the files and navigate to the `distribute` folder
3. Run `install.bat` (Windows) - this will:
   - Install the package from PyPI automatically
   - Set up the environment in your AppData folder
   - Configure the launcher scripts

### MCP Server Configuration

After installation, add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "tableau-mcp": {
      "command": "C:\\Users\\YourUsername\\AppData\\Roaming\\tableau-mcp\\tableau-mcp.bat",
      "env": {
        "GEMINI_API_KEY": "YOUR_KEY_HERE",
        "DEFAULT_LLM_PROVIDER": "gemini"
      }
    }
  }
}
```

**Note**: Get your free Gemini API key at https://aistudio.google.com/apikey

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

- Windows OS (installer provided)
- Python 3.9+
- Gemini API key (free from Google AI Studio)
- Compatible with Claude Desktop and other MCP clients
- Generated workbooks work with Tableau Desktop 2020.1+

## Distribution Package

The complete distribution package includes:
- Automated installation script (`install.bat`)
- Environment setup and dependency management
- Ready-to-use launcher scripts
- Full documentation and examples

Download from: https://github.com/kar10arora/TABLEAU_MCP