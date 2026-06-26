# Tableau MCP - Distribution-Ready Setup Guide

## Current Status: **NOT Distribution-Ready** ⚠️

Your MCP works locally but **hardcoded paths** prevent other users from installing it. This guide fixes that.

---

## Problem Summary

When other users `pip install tableau-mcp-server`, they get:
- ❌ Broken template paths (`./templates` doesn't exist)
- ❌ Hardcoded user paths in documentation
- ❌ Manual configuration required
- ❌ No auto-location of packaged template file

**Solution**: Use proper Python packaging + dynamic path resolution

---

## E2E Steps to Make Distribution-Ready (1-2 hours)

### **PHASE 1: Fix Code Structure** (30 mins)

#### Step 1.1: Create paths resolution module
Create `src/tableau_mcp/paths.py`:

```python
"""Dynamic path resolution for packaged installation."""

import importlib.resources as resources
from pathlib import Path
import os
from typing import Optional


def get_template_path() -> str:
    """
    Get path to Tableau base template.
    Works whether installed via pip or in development.
    
    Returns:
        str: Absolute path to base_template.twb
        
    Raises:
        FileNotFoundError: If template cannot be located
    """
    # Try package resources first (installed via pip)
    try:
        if hasattr(resources, 'files'):  # Python 3.9+
            pkg_resources = resources.files('tableau_mcp')
            template = pkg_resources.joinpath('templates', 'base_template.twb')
            return str(template)
    except (ImportError, FileNotFoundError, AttributeError):
        pass
    
    # Fallback: development environment
    dev_path = Path(__file__).parent.parent / 'templates' / 'base_template.twb'
    if dev_path.exists():
        return str(dev_path)
    
    # Last resort: check current directory
    cwd_path = Path.cwd() / 'templates' / 'base_template.twb'
    if cwd_path.exists():
        return str(cwd_path)
    
    raise FileNotFoundError(
        "Template 'base_template.twb' not found. "
        "Install with: pip install tableau-mcp-server"
    )


def get_output_dir(create: bool = True) -> str:
    """
    Get output directory for generated workbooks.
    
    Args:
        create: Whether to create directory if it doesn't exist
        
    Returns:
        str: Absolute path to output directory
    """
    # Allow override via environment variable
    if env_dir := os.getenv("TABLEAU_OUTPUT_DIR"):
        output_path = Path(env_dir)
    else:
        # Default: user's home directory
        output_path = Path.home() / '.tableau-mcp' / 'workbooks'
    
    if create:
        output_path.mkdir(parents=True, exist_ok=True)
    
    return str(output_path)


def ensure_template_exists() -> bool:
    """
    Verify template file exists and is readable.
    
    Returns:
        bool: True if template is valid
        
    Raises:
        FileNotFoundError: If template cannot be found
    """
    path = get_template_path()
    if not Path(path).exists():
        raise FileNotFoundError(f"Template file not found: {path}")
    return True
```

#### Step 1.2: Update `src/mcp/server.py`

Replace lines 19 and 66:

```python
"""
FastMCP server for Tableau workbook generation.
"""

from fastmcp import FastMCP
from src.core.schema_profiler import SchemaProfiler
from src.core.xml_generator import TableauXMLCompiler
from src.llm.client import LLMClient
from src.tableau_mcp.paths import get_template_path, get_output_dir
import os
import json

# Initialize FastMCP server
mcp = FastMCP("tableau-mcp-server")

# Initialize components
schema_profiler = SchemaProfiler()
llm_client = LLMClient()

# Get paths dynamically (works with pip install)
TEMPLATE_PATH = get_template_path()
DEFAULT_OUTPUT_DIR = get_output_dir(create=True)


@mcp.tool()
def inspect_dataset_schema(file_path: str) -> str:
    """
    Analyze dataset and return schema metadata.
    
    Args:
        file_path: Path to CSV dataset file
        
    Returns:
        JSON string with dimensions and measures
    """
    try:
        schema = schema_profiler.profile_dataset(file_path)
        return json.dumps(schema, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def generate_tableau_workbook(
    dataset_path: str,
    user_request: str,
    output_path: str = None
) -> str:
    """
    Generate complete Tableau workbook from natural language request.
    
    Args:
        dataset_path: Path to CSV dataset
        user_request: Natural language description of desired dashboard
        output_path: Where to save .twb file (optional)
        
    Returns:
        JSON string with generation result
    """
    try:
        # Step 1: Profile dataset
        schema = schema_profiler.profile_dataset(dataset_path)
        
        # Step 2: Generate blueprint with LLM
        blueprint = llm_client.generate_blueprint(schema, user_request)
        
        # Step 3: Compile workbook
        if output_path is None:
            output_path = os.path.join(DEFAULT_OUTPUT_DIR, "generated_workbook.twb")
        
        compiler = TableauXMLCompiler(TEMPLATE_PATH)
        result = compiler.compile_workbook(
            blueprint=blueprint,
            output_path=output_path,
            dataset_path=dataset_path,
            schema=schema,
        )
        
        result["blueprint_used"] = blueprint
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
```

---

### **PHASE 2: Update Package Configuration** (20 mins)

#### Step 2.1: Create `MANIFEST.in`

Create file at project root:

```
recursive-include src/tableau_mcp/templates *.twb
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
include README.md
include LICENSE
include .env.example
```

#### Step 2.2: Update `setup.py`

Replace the entire file:

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tableau-mcp-server",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Model Context Protocol server for automated Tableau workbook generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tableau-mcp-server",
    packages=find_packages(),
    include_package_data=True,  # Include files from MANIFEST.in
    package_data={
        'tableau_mcp': [
            'templates/*.twb',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastmcp>=0.2.0",
        "pandas>=2.0.0",
        "lxml>=4.9.0",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
        "google-generativeai>=0.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    keywords="tableau mcp llm generative-ai dashboard visualization",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/tableau-mcp-server/issues",
        "Documentation": "https://github.com/yourusername/tableau-mcp-server/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/tableau-mcp-server",
    },
)
```

#### Step 2.3: Update `pyproject.toml` (create if doesn't exist)

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "tableau-mcp-server"
version = "1.0.0"
description = "Model Context Protocol server for automated Tableau workbook generation"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [{name = "Your Name", email = "your.email@example.com"}]
keywords = ["tableau", "mcp", "llm", "generative-ai", "dashboard"]

dependencies = [
    "fastmcp>=0.2.0",
    "pandas>=2.0.0",
    "lxml>=4.9.0",
    "python-dotenv>=1.0.0",
    "openai>=1.0.0",
    "google-generativeai>=0.3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
]

[project.urls]
Homepage = "https://github.com/yourusername/tableau-mcp-server"
Documentation = "https://github.com/yourusername/tableau-mcp-server/blob/main/README.md"
Repository = "https://github.com/yourusername/tableau-mcp-server"
Issues = "https://github.com/yourusername/tableau-mcp-server/issues"
```

---

### **PHASE 3: Update User Instructions** (15 mins)

#### Step 3.1: Create `INSTALLATION_FOR_USERS.md`

```markdown
# Installation Guide for Users

## Quick Start (3 steps)

### Step 1: Install the Package
```bash
pip install tableau-mcp-server
```

### Step 2: Add API Key
Create or update `~/.env`:
```
GEMINI_API_KEY=your_key_from_ai.google.dev
DEFAULT_LLM_PROVIDER=gemini
```

Or use OpenRouter:
```
OPENROUTER_API_KEY=your_key_from_openrouter.ai
DEFAULT_LLM_PROVIDER=openrouter
```

### Step 3: Configure Claude Code
Edit `~/.claude/settings.json` and add under `mcpServers`:

```json
{
  "mcpServers": {
    "tableau-generator": {
      "command": "python",
      "args": ["-m", "tableau_mcp.server"],
      "env": {
        "GEMINI_API_KEY": "your_key_here",
        "DEFAULT_LLM_PROVIDER": "gemini"
      }
    }
  }
}
```

That's it! No paths to configure. ✅

### Optional: Custom Output Directory
Generated workbooks go to `~/.tableau-mcp/workbooks/` by default.

To use a custom location:
```json
{
  "mcpServers": {
    "tableau-generator": {
      "command": "python",
      "args": ["-m", "tableau_mcp.server"],
      "env": {
        "GEMINI_API_KEY": "your_key_here",
        "DEFAULT_LLM_PROVIDER": "gemini",
        "TABLEAU_OUTPUT_DIR": "/path/to/your/workbooks"
      }
    }
  }
}
```

### Troubleshooting

**"ModuleNotFoundError: No module named 'tableau_mcp'"**
```bash
pip install --upgrade tableau-mcp-server
```

**"Template not found"**
Reinstall:
```bash
pip uninstall -y tableau-mcp-server && pip install tableau-mcp-server
```

**"API key not found"**
Make sure `GEMINI_API_KEY` is in your `~/.env` and that your shell loads it before Claude Code starts.

---

## Usage

Once configured, use in Claude Code:

```
"Generate a Tableau workbook showing sales by region from my_data.csv"
```

See full documentation: [Full Documentation Link]
```

---

### **PHASE 4: Test Distribution Locally** (20 mins)

#### Step 4.1: Build the package
```bash
cd /Users/kartik.arora/TABLEAU-MCP

# Install build tools
pip install build twine

# Build distribution
python -m build

# This creates:
# - dist/tableau-mcp-server-1.0.0.tar.gz (source)
# - dist/tableau-mcp-server-1.0.0-py3-none-any.whl (binary)
```

#### Step 4.2: Test installation in clean environment
```bash
# Create test environment
python -m venv /tmp/test_tableau_env
source /tmp/test_tableau_env/bin/activate

# Install from local build
pip install /Users/kartik.arora/TABLEAU-MCP/dist/tableau-mcp-server-1.0.0-py3-none-any.whl

# Test import
python -c "from tableau_mcp.server import mcp; print('✅ Import successful')"

# Verify template is found
python -c "from tableau_mcp.paths import get_template_path; print(f'Template: {get_template_path()}')"

# Verify output dir is created
python -c "from tableau_mcp.paths import get_output_dir; print(f'Output: {get_output_dir()}')"
```

#### Step 4.3: Test MCP server starts
```bash
python -m tableau_mcp.server
# Should output: INFO: Started server process...
```

---

## Before Distribution

### Checklist
- [ ] All hardcoded paths removed
- [ ] `paths.py` created with smart path resolution
- [ ] `src/mcp/server.py` updated to use new paths
- [ ] `setup.py` updated with `include_package_data=True`
- [ ] `MANIFEST.in` created
- [ ] `pyproject.toml` created
- [ ] Package builds successfully: `python -m build`
- [ ] Test installation works in clean environment
- [ ] Template is found after pip install
- [ ] User instructions are clear (no hardcoded paths)

---

## Distribution Methods

### Option A: GitHub (Recommended)
```bash
# 1. Push to GitHub
git remote add origin https://github.com/yourusername/tableau-mcp-server.git
git push -u origin main

# 2. Create GitHub release
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0

# 3. Users install with:
pip install git+https://github.com/yourusername/tableau-mcp-server.git
```

### Option B: PyPI (Official)
```bash
# 1. Register on PyPI
# 2. Create ~/.pypirc with credentials
# 3. Upload package
python -m twine upload dist/*

# 4. Users install with:
pip install tableau-mcp-server
```

### Option C: Private Package (Internal)
Host on private PyPI or Artifactory

---

## Architecture After Distribution-Ready

```
User's System
├── ~/.tableau-mcp/
│   ├── workbooks/          (auto-created output)
│   └── .env                (API keys)
│
├── ~/.claude/
│   └── settings.json       (MCP config, NO PATHS)
│
└── venv/lib/python3.x/
    └── site-packages/
        └── tableau_mcp/
            ├── server.py   (uses paths.py for resolution)
            ├── paths.py    (smart path resolution)
            ├── core/
            │   ├── schema_profiler.py
            │   ├── xml_generator.py
            │   └── uuid_utils.py
            ├── llm/
            │   └── client.py
            └── templates/
                └── base_template.twb  (packaged with code)
```

All paths are **dynamic** and **user-independent** ✅

---

## Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Path handling** | Hardcoded/relative | Smart resolution |
| **Template location** | Not packaged | In site-packages |
| **Output directory** | Requires config | Auto ~/.tableau-mcp |
| **User config** | Paths required | API key only |
| **Pip installation** | Broken | Works perfectly |
| **Distribution** | Not possible | Ready for PyPI |

**Estimated time to complete**: 1-2 hours  
**Complexity**: Medium (mostly refactoring)  
**Result**: Professional, distribution-ready MCP 🚀
