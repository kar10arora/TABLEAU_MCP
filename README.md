# Tableau MCP Server

> Automated Tableau dashboard generation through natural language using AI

## Overview
Tableau MCP Server is a Model Context Protocol (MCP) server that enables automatic Tableau workbook generation from natural language requests. Integrated with Claude Desktop and Kiro IDE, it transforms simple text descriptions into professional Tableau dashboards.

## 🎯 Key Features

- **Natural Language Interface**: Describe dashboards in plain English
- **Automated Generation**: Creates valid `.twb` files instantly
- **Multiple Chart Types**: Bar, line, area, scatter, text KPIs
- **Advanced Features**: Calculated fields, dashboards, filtering, sorting
- **Enterprise Ready**: Multi-datasource, templates, cloud deployment
- **100% Valid Output**: Pre-validated XML templates ensure workbooks always open

## 📚 Documentation

### Core Documents
- **[Product Requirements (PRD)](./TABLEAU_MCP_PRD.md)**: Complete product specification
- **[Architecture](./ARCHITECTURE_DIAGRAM.md)**: Technical design and system architecture
- **[Implementation Guide](./IMPLEMENTATION_GUIDE.md)**: Step-by-step development instructions
- **[Project Roadmap](./PROJECT_ROADMAP.md)**: 4-month development timeline

### Epic & Story Documentation
Detailed implementation stories organized by development phase:
- **[Epic 1: MVP Foundation](./docs/epic-01-mvp-foundation/)** - Core system (4 weeks)
- **[Epic 2: Enhanced Visualizations](./docs/epic-02-enhanced-visualizations/)** - Chart types (4 weeks)
- **[Epic 3: Advanced Features](./docs/epic-03-advanced-features/)** - Dashboards, calculations (4 weeks)
- **[Epic 4: Enterprise & Scale](./docs/epic-04-enterprise-scale/)** - Production deployment (4 weeks)

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Tableau Desktop 2020.1+ (for validation)
- LLM API access (Gemini or OpenRouter)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/tableau-mcp-server.git
cd tableau-mcp-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys
```

### Create Base Template

**IMPORTANT**: You must create the base template manually:

1. Open Tableau Desktop
2. Connect to any simple CSV dataset
3. Create a blank worksheet (don't add any fields)
4. Save As: `templates/base_blank.twb`
   - **Must be `.twb` format** (NOT `.twbx`)

### Run the Server

```bash
python src/mcp/server.py
```

### Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tableau-generator": {
      "command": "python",
      "args": ["/absolute/path/to/tableau-mcp-server/src/mcp/server.py"],
      "env": {
        "GEMINI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## 📖 Usage Examples

### Generate a Simple Bar Chart
```
User: "Generate a bar chart showing sales by category from /path/to/sales.csv"

Result: Creates workbook with bar chart at examples/generated_workbooks/generated_workbook.twb
```

### Create a Multi-Sheet Dashboard
```
User: "Create a dashboard with:
      - Sales trend over time (line chart)
      - Top 10 products (bar chart)  
      - Total revenue KPI"

Result: Creates workbook with 3 sheets combined in a dashboard
```

### Inspect Dataset
```
User: "What fields are in my dataset at /path/to/data.csv?"

Result: Returns schema with dimensions and measures
```

## 🏗️ Project Structure

```
tableau-mcp-server/
├── src/
│   ├── core/              # Core modules
│   │   ├── uuid_utils.py
│   │   ├── schema_profiler.py
│   │   ├── xml_generator.py
│   │   └── field_resolver.py
│   ├── mcp/               # MCP server
│   │   ├── server.py
│   │   └── tools.py
│   └── llm/               # LLM integration
│       └── client.py
│
├── tests/                 # Test suite
├── templates/             # Tableau templates (add base_blank.twb here)
├── examples/
│   ├── sample_datasets/   # Test CSV files
│   └── generated_workbooks/  # Output directory
│
├── docs/                  # Epic/story documentation
│   ├── epic-01-mvp-foundation/
│   ├── epic-02-enhanced-visualizations/
│   ├── epic-03-advanced-features/
│   └── epic-04-enterprise-scale/
│
├── requirements.txt
├── .env.example
└── README.md
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific tests
pytest tests/test_uuid_utils.py -v
```

## 🛠️ Technology Stack

- **Backend**: Python 3.9+, FastMCP, lxml, pandas
- **LLM**: Google Gemini, OpenRouter (Claude, GPT)
- **Tableau**: .twb XML format, Tableau Desktop/Server
- **Testing**: pytest, pytest-cov
- **Deployment**: Docker, Kubernetes

## 📊 Development Roadmap

| Phase | Duration | Features | Status |
|-------|----------|----------|--------|
| **Phase 1: MVP** | 4 weeks | Basic bar charts, MCP integration | 🎯 Ready to Start |
| **Phase 2: Enhanced** | 4 weeks | Multiple chart types, filtering, sorting | 📋 Planned |
| **Phase 3: Advanced** | 4 weeks | Calculated fields, dashboards, publishing | 📋 Planned |
| **Phase 4: Enterprise** | 4 weeks | Multi-datasource, templates, production | 📋 Planned |

**Total Timeline**: 16 weeks (~4 months)

## 🔒 Architecture Principles

### Critical Design Rules
1. **LLM NEVER writes raw XML** - only generates JSON blueprints
2. **Template-based injection** ensures 100% valid workbooks
3. **UUID uniqueness** is mandatory (Tableau requirement)
4. **Field names must match schema** exactly
5. **Pre-validated templates** prevent syntax errors

### System Flow
```
User Request → MCP Tool → Schema Profiler → LLM (JSON Blueprint) 
→ XML Generator → Safe Injection → .twb File → Tableau Desktop
```

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Follow code style (black, flake8)
4. Add tests for new features
5. Submit a pull request

### Development Setup
```bash
pip install -e ".[dev]"
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Support & Resources

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## 🎉 Acknowledgments

- Tableau for the visualization platform
- Anthropic for MCP protocol and Claude
- Google for Gemini API
- Open source community

---

**Status**: ✅ Ready for Phase 1 Implementation  
**Next Steps**: Begin Story 1.1 (Project Setup) from Epic 1

Let's build something amazing! 🚀
