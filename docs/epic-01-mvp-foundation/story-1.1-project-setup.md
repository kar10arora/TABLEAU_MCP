# Story 1.1: Project Setup & Infrastructure

## Story Details
**Epic**: Epic 1 - MVP Foundation  
**Story Points**: 3  
**Priority**: P0 (Critical)  
**Assignee**: TBD  
**Sprint**: Week 1

## User Story
**As a** developer  
**I want** a properly structured project with all dependencies configured  
**So that** I can start implementing core features immediately

## Acceptance Criteria
- [ ] Git repository initialized with proper .gitignore
- [ ] Python virtual environment created and documented
- [ ] All required dependencies installed (requirements.txt)
- [ ] Project directory structure created following architecture
- [ ] Environment variables configured (.env file)
- [ ] README.md with setup instructions
- [ ] Code style tools configured (black, flake8)
- [ ] pytest configured for testing

## Technical Details

### Project Structure
```
tableau-mcp-server/
├── README.md
├── requirements.txt
├── setup.py
├── .gitignore
├── .env.example
├── .env (not in git)
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── uuid_utils.py
│   │   ├── schema_profiler.py
│   │   ├── xml_generator.py
│   │   └── field_resolver.py
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── tools.py
│   └── llm/
│       ├── __init__.py
│       └── client.py
│
├── templates/
│   └── (base_blank.twb will be added by user)
│
├── tests/
│   ├── __init__.py
│   ├── test_uuid_utils.py
│   ├── test_schema_profiler.py
│   ├── test_xml_generator.py
│   ├── test_llm_client.py
│   └── test_integration.py
│
├── examples/
│   ├── sample_datasets/
│   │   └── (sample CSVs)
│   └── generated_workbooks/
│       └── (output directory)
│
└── docs/
    └── (epic and story documentation)
```

### Dependencies (requirements.txt)
```python
# Core
fastmcp>=0.2.0
pandas>=2.0.0
lxml>=4.9.0
python-dotenv>=1.0.0

# LLM
openai>=1.0.0
google-generativeai>=0.3.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0

# Development
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
```

### Environment Variables (.env.example)
```bash
# LLM API Keys (choose one or both)
OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# Default provider
DEFAULT_LLM_PROVIDER=gemini

# Paths
TEMPLATE_DIR=./templates
OUTPUT_DIR=./examples/generated_workbooks

# Settings
MAX_CSV_ROWS_TO_PROFILE=100
MAX_FILE_SIZE_MB=500
LOG_LEVEL=INFO
```

## Implementation Tasks
- [ ] Create repository structure
- [ ] Initialize git and add .gitignore
- [ ] Create requirements.txt with all dependencies
- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Create .env.example and .env
- [ ] Set up pytest configuration
- [ ] Configure black and flake8
- [ ] Create initial README.md
- [ ] Create all __init__.py files
- [ ] Verify setup by running `pytest` (should find 0 tests)

## Testing Strategy
- Verify all directories created
- Verify all dependencies install without errors
- Verify pytest runs successfully
- Verify import paths work (import src.core.uuid_utils)

## Documentation
- README.md with setup instructions
- .env.example with all variables explained
- setup.py with project metadata

## Definition of Done
- [ ] All directories and files created
- [ ] Dependencies install cleanly
- [ ] Virtual environment documented
- [ ] README covers setup completely
- [ ] Code style tools configured
- [ ] pytest configuration works
- [ ] Team can clone and set up in <10 minutes

## Related Stories
- **Blocks**: All other stories in Epic 1
- **Depends On**: None

## Notes
- Use Python 3.9+ for compatibility
- Keep requirements.txt minimal (only production deps)
- Document any OS-specific setup issues
