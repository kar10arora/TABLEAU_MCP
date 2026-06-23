# Tableau MCP Server - Setup Guide

## ✅ What's Complete

You've successfully completed **Story 1.1 through 1.4** from Epic 1:

- ✅ Project structure created
- ✅ Git repository initialized
- ✅ Virtual environment set up
- ✅ Dependencies installed
- ✅ Core modules implemented:
  - `src/core/uuid_utils.py` - UUID generation
  - `src/core/schema_profiler.py` - Dataset profiling
  - `src/core/xml_generator.py` - Workbook generation
- ✅ Test suite created (13 tests, all passing)
- ✅ Sample dataset created
- ✅ Base template added (`templates/base_template.twb`)
- ✅ Basic demo working (without LLM)

## 🎯 Current Status

**Phase**: Epic 1 - MVP Foundation  
**Progress**: Stories 1.1-1.4 complete (4/7)  
**Next**: Story 1.5 - LLM Integration

## 📋 Next Steps

### 1. Set Up API Keys (for LLM Integration)

To enable natural language workbook generation, you need an LLM API key:

**Option A: Google Gemini (Recommended - Free tier available)**
```bash
# Create .env file
cp .env.example .env

# Add your Gemini API key to .env
GEMINI_API_KEY=your_actual_key_here
DEFAULT_LLM_PROVIDER=gemini
```

Get a free Gemini API key: https://makersuite.google.com/app/apikey

**Option B: OpenRouter (Alternative)**
```bash
# Add to .env
OPENROUTER_API_KEY=your_actual_key_here
DEFAULT_LLM_PROVIDER=openrouter
```

Get OpenRouter key: https://openrouter.ai/

### 2. Test the Complete Pipeline

Once you have API keys set up:

```bash
# Test with LLM integration
python demo_with_llm.py
```

This will test the full natural language → workbook pipeline.

### 3. Set Up MCP Integration (Claude Desktop or Kiro)

**For Claude Desktop:**

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tableau-generator": {
      "command": "python",
      "args": ["/absolute/path/to/your/TABLEAU-MCP/src/mcp/server.py"],
      "env": {
        "GEMINI_API_KEY": "your_key_here"
      }
    }
  }
}
```

Replace `/absolute/path/to/your/TABLEAU-MCP` with your actual path.

**For Kiro IDE:**

Similar configuration through Kiro's MCP settings.

## 🧪 Testing

### Run All Tests
```bash
source venv/bin/activate
pytest tests/ -v
```

### Run Specific Tests
```bash
# UUID tests
pytest tests/test_uuid_utils.py -v

# Schema profiler tests
pytest tests/test_schema_profiler.py -v

# XML generator tests
pytest tests/test_xml_generator.py -v
```

### Test Coverage
```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## 📊 Demo Scripts

### Basic Demo (No LLM Required)
```bash
python demo_basic.py
```

Generates a workbook with hardcoded blueprint. Output: `examples/generated_workbooks/demo_basic.twb`

### Full Demo (Requires LLM API Key)
```bash
python demo_with_llm.py  # Coming next
```

Uses natural language to generate workbooks.

## 🔍 Verify Generated Workbook

1. Open Tableau Desktop
2. File → Open
3. Navigate to `examples/generated_workbooks/demo_basic.twb`
4. Verify the two sheets load correctly:
   - "Sales by Region" - Bar chart
   - "Sales by Category" - Bar chart

## 📚 Project Structure

```
TABLEAU-MCP/
├── src/
│   ├── core/
│   │   ├── uuid_utils.py          ✅ Complete
│   │   ├── schema_profiler.py     ✅ Complete
│   │   └── xml_generator.py       ✅ Complete
│   ├── llm/
│   │   └── client.py               ✅ Complete (needs API key)
│   └── mcp/
│       └── server.py               ✅ Complete (needs API key)
│
├── tests/                          ✅ 13 tests passing
├── examples/
│   ├── sample_datasets/
│   │   └── sales_sample.csv        ✅ Created
│   └── generated_workbooks/
│       └── demo_basic.twb          ✅ Generated
│
├── templates/
│   └── base_template.twb           ✅ Added by you
│
├── demo_basic.py                   ✅ Working
├── requirements.txt                ✅ Complete
├── .env.example                    ✅ Complete
└── README.md                       ✅ Complete
```

## 🚀 What You Can Do Now

### Without LLM API Key:
- ✅ Generate workbooks with hardcoded blueprints
- ✅ Profile datasets
- ✅ Run all tests
- ✅ Understand the complete architecture

### With LLM API Key:
- 🎯 Generate workbooks from natural language
- 🎯 Use MCP tools in Claude Desktop/Kiro
- 🎯 Full end-to-end pipeline

## ⏭️ Next Implementation Steps

Follow the story documentation in order:

1. **Story 1.5**: LLM Integration (needs API key)
   - File: `docs/epic-01-mvp-foundation/story-1.5-llm-integration.md`
   - Status: Code complete, needs API key for testing

2. **Story 1.6**: MCP Server Implementation
   - File: `docs/epic-01-mvp-foundation/story-1.6-mcp-server.md`
   - Status: Code complete, needs API key for testing

3. **Story 1.7**: Testing & Validation
   - File: `docs/epic-01-mvp-foundation/story-1.7-testing.md`
   - Status: Basic tests complete, integration tests need API key

## 💡 Tips

- Keep your API keys in `.env` file (never commit to git)
- Test with small datasets first
- Always verify workbooks open in Tableau Desktop
- Check logs if generation fails
- Reference `IMPLEMENTATION_GUIDE.md` for code examples

## 🆘 Troubleshooting

**Workbook won't open in Tableau:**
- Check that template file exists and is valid `.twb` format
- Verify dataset path is correct
- Check for XML syntax errors in generated file

**Tests failing:**
- Ensure you're in virtual environment: `source venv/bin/activate`
- Check all dependencies installed: `pip install -r requirements.txt`
- Verify template exists: `ls templates/base_template.twb`

**Import errors:**
- Make sure you're running from project root
- Python path should include `src/` directory

---

**Status**: ✅ MVP Foundation 60% Complete (4/7 stories)  
**Next**: Add API key to complete LLM integration
