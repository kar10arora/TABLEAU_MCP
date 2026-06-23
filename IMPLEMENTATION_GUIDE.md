# Tableau MCP - Complete Implementation Guide
## From Zero to Production Deployment

---

## TABLE OF CONTENTS

1. [Project Setup](#1-project-setup)
2. [Phase 1: MVP Implementation](#2-phase-1-mvp-implementation)
3. [Phase 2: Enhanced Features](#3-phase-2-enhanced-features)
4. [Phase 3: Advanced Capabilities](#4-phase-3-advanced-capabilities)
5. [Testing & Validation](#5-testing--validation)
6. [Deployment](#6-deployment)
7. [User Documentation](#7-user-documentation)

---

## 1. PROJECT SETUP

### 1.1 Prerequisites

**Required Software**:
- Python 3.9 or higher
- Tableau Desktop 2020.1+ (for validation)
- Git
- Code editor (VS Code recommended)

**Required Accounts**:
- OpenRouter API account (free tier) OR
- Google Gemini API account (free tier)
- GitHub account (for version control)

### 1.2 Initial Repository Setup

```bash
# Create project directory
mkdir tableau-mcp-server
cd tableau-mcp-server

# Initialize git repository
git init

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create project structure
mkdir -p src/core src/mcp src/llm tests templates examples/sample_datasets examples/generated_workbooks

# Create initial files
touch README.md requirements.txt setup.py .gitignore
touch src/__init__.py src/core/__init__.py src/mcp/__init__.py src/llm/__init__.py
```

### 1.3 Requirements.txt

```python
# Core dependencies
fastmcp>=0.2.0
pandas>=2.0.0
lxml>=4.9.0
python-dotenv>=1.0.0

# LLM integrations
openai>=1.0.0  # For OpenRouter
google-generativeai>=0.3.0  # For Gemini

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0

# Development
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 1.4 Environment Configuration

Create `.env` file:
```bash
# LLM API Keys (choose one or both)
OPENROUTER_API_KEY=your_openrouter_key_here
GEMINI_API_KEY=your_gemini_key_here

# Default LLM provider (openrouter or gemini)
DEFAULT_LLM_PROVIDER=gemini

# Paths
TEMPLATE_DIR=./templates
OUTPUT_DIR=./examples/generated_workbooks

# Settings
MAX_CSV_ROWS_TO_PROFILE=100
MAX_FILE_SIZE_MB=500
```

### 1.5 .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Generated files
examples/generated_workbooks/*.twb
*.log

# OS
.DS_Store
Thumbs.db
```

---

## 2. PHASE 1: MVP IMPLEMENTATION

### 2.1 Core Module: UUID Utils

**File**: `src/core/uuid_utils.py`

```python
"""
UUID generation utilities for Tableau workbooks.
Ensures all worksheets and windows have unique identifiers.
"""

import uuid
from typing import Dict, List


class UUIDManager:
    """Manages UUID generation and tracking for Tableau elements."""
    
    def __init__(self):
        self._generated_uuids: List[str] = []
    
    def generate_tableau_uuid(self) -> str:
        """
        Generate a unique, uppercase UUID in Tableau format.
        
        Returns:
            str: UUID in format {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}
        """
        new_uuid = f"{{{str(uuid.uuid4()).upper()}}}"
        
        # Ensure uniqueness (extremely rare collision, but safe check)
        while new_uuid in self._generated_uuids:
            new_uuid = f"{{{str(uuid.uuid4()).upper()}}}"
        
        self._generated_uuids.append(new_uuid)
        return new_uuid
    
    def generate_pair(self) -> Dict[str, str]:
        """
        Generate a matched pair of UUIDs for worksheet and window.
        
        Returns:
            dict: {"worksheet_uuid": str, "window_uuid": str}
        """
        return {
            "worksheet_uuid": self.generate_tableau_uuid(),
            "window_uuid": self.generate_tableau_uuid()
        }
    
    def reset(self):
        """Clear all generated UUIDs. Use with caution."""
        self._generated_uuids.clear()


# Global instance for easy import
uuid_manager = UUIDManager()


def generate_tableau_uuid() -> str:
    """Convenience function using global UUID manager."""
    return uuid_manager.generate_tableau_uuid()
```

### 2.2 Core Module: Schema Profiler

**File**: `src/core/schema_profiler.py`

```python
"""
Dataset schema profiling module.
Extracts metadata from CSV files without loading entire dataset.
"""

import pandas as pd
from typing import Dict, List, Optional
import os


class SchemaProfiler:
    """Profiles datasets to extract dimensions and measures."""
    
    def __init__(self, max_rows: int = 100):
        """
        Initialize profiler.
        
        Args:
            max_rows: Maximum rows to read for schema detection
        """
        self.max_rows = max_rows
    
    def profile_dataset(self, file_path: str) -> Dict:
        """
        Extract schema metadata from CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            dict: Schema metadata with dimensions and measures
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file cannot be parsed
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset not found: {file_path}")
        
        try:
            # Read only first N rows for efficiency
            df = pd.read_csv(file_path, nrows=self.max_rows)
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")
        
        schema = {
            "file_name": os.path.basename(file_path),
            "absolute_path": os.path.abspath(file_path),
            "dimensions": [],
            "measures": [],
            "total_columns": len(df.columns),
            "sample_row_count": len(df)
        }
        
        for column in df.columns:
            column_info = {
                "name": column,
                "sample_values": df[column].dropna().head(3).tolist()
            }
            
            # Classify as measure or dimension based on dtype
            if df[column].dtype in ['int64', 'float64']:
                column_info["type"] = "quantitative"
                column_info["default_aggregation"] = "Sum"
                schema["measures"].append(column_info)
            else:
                column_info["type"] = "nominal"
                column_info["cardinality"] = df[column].nunique()
                schema["dimensions"].append(column_info)
        
        return schema
    
    def validate_field_name(self, field_name: str, schema: Dict) -> bool:
        """
        Check if field name exists in schema.
        
        Args:
            field_name: Name of field to validate
            schema: Schema dict from profile_dataset()
            
        Returns:
            bool: True if field exists
        """
        all_fields = [d["name"] for d in schema["dimensions"]] + \
                    [m["name"] for m in schema["measures"]]
        
        return field_name in all_fields
    
    def get_field_type(self, field_name: str, schema: Dict) -> Optional[str]:
        """
        Get type of field (dimension or measure).
        
        Args:
            field_name: Name of field
            schema: Schema dict from profile_dataset()
            
        Returns:
            str: "dimension", "measure", or None if not found
        """
        if any(d["name"] == field_name for d in schema["dimensions"]):
            return "dimension"
        if any(m["name"] == field_name for m in schema["measures"]):
            return "measure"
        return None


# Convenience function
def profile_dataset(file_path: str) -> Dict:
    """Quick schema profiling with defaults."""
    profiler = SchemaProfiler()
    return profiler.profile_dataset(file_path)
```

### 2.3 Core Module: XML Generator

**File**: `src/core/xml_generator.py`

```python
"""
Tableau XML workbook generator.
Safely manipulates .twb files using template injection.
"""

from lxml import etree
from typing import Dict, List, Optional
import os
from src.core.uuid_utils import generate_tableau_uuid


class TableauXMLCompiler:
    """Compiles Tableau workbooks from JSON blueprints."""
    
    def __init__(self, template_path: str):
        """
        Initialize compiler with template.
        
        Args:
            template_path: Path to base .twb template file
        """
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        self.template_path = template_path
        self.parser = etree.XMLParser(remove_blank_text=False, recover=True)
    
    def compile_workbook(self, 
                        blueprint: Dict, 
                        output_path: str,
                        dataset_path: str = None) -> Dict:
        """
        Generate complete .twb workbook from blueprint.
        
        Args:
            blueprint: JSON blueprint with sheets configuration
            output_path: Where to save generated .twb file
            dataset_path: Path to dataset (for datasource update)
            
        Returns:
            dict: {"success": bool, "workbook_path": str, "sheets_created": int}
        """
        # Load template
        tree = etree.parse(self.template_path, self.parser)
        root = tree.getroot()
        
        # Extract datasource ID
        datasource_elem = root.find(".//datasources/datasource")
        if datasource_elem is None:
            raise ValueError("Template missing datasource element")
        
        ds_id = datasource_elem.get("name")
        
        # Update dataset path if provided
        if dataset_path:
            self._update_datasource_path(root, dataset_path)
        
        # Get parent containers
        worksheets_parent = root.find(".//worksheets")
        windows_parent = root.find(".//windows")
        
        if worksheets_parent is None or windows_parent is None:
            raise ValueError("Template missing worksheets or windows container")
        
        # Clear existing sheets
        worksheets_parent.clear()
        windows_parent.clear()
        windows_parent.set("source-height", "30")
        
        # Generate sheets from blueprint
        sheets_created = 0
        for index, sheet in enumerate(blueprint.get("sheets", [])):
            try:
                # Generate UUIDs
                sheet_uuid = generate_tableau_uuid()
                window_uuid = generate_tableau_uuid()
                
                # Build worksheet XML
                worksheet_xml = self._build_worksheet(
                    name=sheet["name"],
                    ds_id=ds_id,
                    cols=sheet.get("column_field", ""),
                    rows=sheet.get("row_field", ""),
                    mark_type=sheet.get("mark_type", "Automatic"),
                    uuid=sheet_uuid
                )
                
                # Build window XML
                window_xml = self._build_window(
                    name=sheet["name"],
                    uuid=window_uuid,
                    maximized=(index == 0)  # Maximize first sheet
                )
                
                # Inject into tree
                worksheets_parent.append(etree.fromstring(worksheet_xml, self.parser))
                windows_parent.append(etree.fromstring(window_xml, self.parser))
                
                sheets_created += 1
                
            except Exception as e:
                print(f"Warning: Failed to create sheet '{sheet.get('name')}': {str(e)}")
                continue
        
        # Write final workbook
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        return {
            "success": True,
            "workbook_path": output_path,
            "sheets_created": sheets_created
        }
    
    def _build_worksheet(self, name: str, ds_id: str, cols: str, rows: str, 
                        mark_type: str, uuid: str) -> str:
        """Build worksheet XML block safely."""
        
        # Construct field references
        cols_ref = f"[{ds_id}].[{cols}]" if cols else ""
        rows_ref = f"[{ds_id}].[{rows}]" if rows else ""
        
        worksheet_xml = f"""
        <worksheet name='{name}'>
          <table>
            <view>
              <datasources>
                <datasource name='{ds_id}' />
              </datasources>
              <datasource-dependencies datasource='{ds_id}'>
                <column datatype='string' name='[{cols}]' role='dimension' type='nominal' />
                <column datatype='real' name='[{rows}]' role='measure' type='quantitative' />
              </datasource-dependencies>
              <aggregation value='true' />
            </view>
            <style />
            <panes>
              <pane selection-relaxation-option='selection-relaxation-allow'>
                <view>
                  <breakdown value='auto' />
                </view>
                <mark class='{mark_type}' />
              </pane>
            </panes>
            <rows>{rows_ref}</rows>
            <cols>{cols_ref}</cols>
          </table>
          <simple-id uuid='{uuid}' />
        </worksheet>
        """
        return worksheet_xml
    
    def _build_window(self, name: str, uuid: str, maximized: bool = False) -> str:
        """Build window XML block safely."""
        
        maximized_attr = "maximized='true'" if maximized else ""
        
        window_xml = f"""
        <window class='worksheet' {maximized_attr} name='{name}'>
          <cards>
            <edge name='left'>
              <strip size='160'>
                <card type='pages' />
                <card type='filters' />
                <card type='marks' />
              </strip>
            </edge>
            <edge name='top'>
              <strip size='2147483647'>
                <card type='columns' />
              </strip>
              <strip size='2147483647'>
                <card type='rows' />
              </strip>
              <strip size='31'>
                <card type='title' />
              </strip>
            </edge>
          </cards>
          <simple-id uuid='{uuid}' />
        </window>
        """
        return window_xml
    
    def _update_datasource_path(self, root, dataset_path: str):
        """Update datasource connection to point to new dataset."""
        connection_elem = root.find(".//connection[@class='textscan']")
        if connection_elem is not None:
            connection_elem.set("directory", os.path.dirname(dataset_path))
            connection_elem.set("filename", os.path.basename(dataset_path))
```

### 2.4 LLM Integration Module

**File**: `src/llm/client.py`

```python
"""
LLM integration for blueprint generation.
Supports OpenRouter and Google Gemini.
"""

import json
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Client for interacting with LLM APIs."""
    
    def __init__(self, provider: str = None):
        """
        Initialize LLM client.
        
        Args:
            provider: "openrouter" or "gemini". Defaults to env variable.
        """
        self.provider = provider or os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
        
        if self.provider == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError("OPENROUTER_API_KEY not set in environment")
        elif self.provider == "gemini":
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not set in environment")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def generate_blueprint(self, schema: Dict, user_request: str) -> Dict:
        """
        Generate JSON blueprint from schema and user request.
        
        Args:
            schema: Dataset schema from SchemaProfiler
            user_request: Natural language request from user
            
        Returns:
            dict: JSON blueprint with sheets configuration
        """
        prompt = self._build_prompt(schema, user_request)
        
        if self.provider == "gemini":
            return self._call_gemini(prompt)
        elif self.provider == "openrouter":
            return self._call_openrouter(prompt)
    
    def _build_prompt(self, schema: Dict, user_request: str) -> str:
        """Construct prompt for LLM."""
        
        dimensions_list = [d["name"] for d in schema["dimensions"]]
        measures_list = [m["name"] for m in schema["measures"]]
        
        prompt = f"""You are a Tableau dashboard generator. Given a dataset schema and user request, generate a JSON blueprint for creating Tableau worksheets.

Dataset Schema:
- Dimensions (categorical fields): {', '.join(dimensions_list)}
- Measures (numeric fields): {', '.join(measures_list)}

User Request: {user_request}

Generate a JSON blueprint following this EXACT format (no additional text):
{{
  "sheets": [
    {{
      "name": "Sheet 1",
      "column_field": "<choose dimension>",
      "row_field": "<choose measure>",
      "mark_type": "Bar"
    }}
  ]
}}

Rules:
1. Use ONLY field names from the schema above
2. column_field should be a dimension
3. row_field should be a measure
4. mark_type can be: Bar, Line, Area, or Automatic
5. Create 1-3 sheets based on the request
6. Return ONLY valid JSON, no explanations

Generate the blueprint now:"""
        
        return prompt
    
    def _call_gemini(self, prompt: str) -> Dict:
        """Call Google Gemini API."""
        import google.generativeai as genai
        
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON from response
        try:
            # Try to find JSON in response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            blueprint = json.loads(response_text)
            return blueprint
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON: {response_text[:200]}...")
    
    def _call_openrouter(self, prompt: str) -> Dict:
        """Call OpenRouter API."""
        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )
        
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",  # or other free models
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.choices[0].message.content.strip()
        
        try:
            blueprint = json.loads(response_text)
            return blueprint
        except json.JSONDecodeError:
            raise ValueError(f"LLM returned invalid JSON: {response_text[:200]}...")
```

### 2.5 MCP Server Implementation

**File**: `src/mcp/server.py`

```python
"""
FastMCP server for Tableau workbook generation.
"""

from fastmcp import FastMCP
from src.core.schema_profiler import SchemaProfiler
from src.core.xml_generator import TableauXMLCompiler
from src.llm.client import LLMClient
import os
import json

# Initialize FastMCP server
mcp = FastMCP("tableau-mcp-server")

# Initialize components
schema_profiler = SchemaProfiler()
llm_client = LLMClient()

TEMPLATE_PATH = os.getenv("TEMPLATE_DIR", "./templates") + "/base_blank.twb"


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
            output_dir = os.getenv("OUTPUT_DIR", "./examples/generated_workbooks")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "generated_workbook.twb")
        
        compiler = TableauXMLCompiler(TEMPLATE_PATH)
        result = compiler.compile_workbook(
            blueprint=blueprint,
            output_path=output_path,
            dataset_path=dataset_path
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

### 2.6 Testing the MVP

**File**: `tests/test_mvp.py`

```python
"""
MVP integration tests.
"""

import pytest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.schema_profiler import SchemaProfiler
from src.core.xml_generator import TableauXMLCompiler
from src.core.uuid_utils import generate_tableau_uuid


def test_uuid_generation():
    """Test UUID generation is unique and properly formatted."""
    uuid1 = generate_tableau_uuid()
    uuid2 = generate_tableau_uuid()
    
    assert uuid1 != uuid2
    assert uuid1.startswith('{')
    assert uuid1.endswith('}')
    assert len(uuid1) == 38  # {XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}


def test_schema_profiling():
    """Test dataset schema profiling."""
    # Create sample CSV
    sample_csv = "tests/sample.csv"
    with open(sample_csv, "w") as f:
        f.write("category,price,quantity\n")
        f.write("A,100,5\n")
        f.write("B,200,3\n")
    
    profiler = SchemaProfiler()
    schema = profiler.profile_dataset(sample_csv)
    
    assert len(schema["dimensions"]) == 1
    assert schema["dimensions"][0]["name"] == "category"
    assert len(schema["measures"]) == 2
    assert "price" in [m["name"] for m in schema["measures"]]
    
    # Cleanup
    os.remove(sample_csv)


def test_workbook_generation():
    """Test complete workbook generation."""
    # This requires a valid template file
    # See next section for template creation
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 2.7 Running the MVP

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run tests
pytest tests/ -v

# Start MCP server
python src/mcp/server.py
```

**Connecting to MCP Host (Claude Desktop)**:

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

---

## 3. CREATING THE BASE TEMPLATE

### 3.1 Manual Template Creation

1. **Open Tableau Desktop**
2. **Connect to Data**: File → New → Connect to Data → Text File
3. **Select any simple CSV** (e.g., Sample - Superstore)
4. **Create blank worksheet**: Don't add any fields
5. **Save As**: File → Save As
   - **IMPORTANT**: Save as `.twb` (NOT `.twbx`)
   - Save to: `templates/base_blank.twb`

This template will be the foundation for all generated workbooks.

---

## 4. PHASE 2 & 3 ENHANCEMENTS

(Implementation details for advanced features to be added in subsequent iterations)

---

## 5. USAGE EXAMPLES

### Example 1: Simple Bar Chart

```python
# In Claude Desktop / Kiro chat:
User: "I have a dataset at /path/to/sales.csv. 
       Create a bar chart showing total sales by region."

# MCP Server will:
# 1. Profile the dataset
# 2. Generate blueprint with LLM
# 3. Create workbook at ./examples/generated_workbooks/generated_workbook.twb
# 4. Return success message with path
```

### Example 2: Multiple Sheets

```python
User: "Generate a dashboard with:
       1. Sales by category (bar chart)
       2. Profit trend over time (line chart)
       3. Top 10 products (horizontal bar)"
       
# MCP will create a workbook with 3 sheets
```

---

## 6. TROUBLESHOOTING

### Common Issues:

**Issue 1**: "Template not found"
```bash
# Solution: Create template manually in Tableau Desktop
# Save as base_blank.twb in templates/ directory
```

**Issue 2**: "LLM returned invalid JSON"
```bash
# Solution: Check LLM provider is working
# Try simpler request
# Check API key is valid
```

**Issue 3**: "Generated workbook won't open in Tableau"
```bash
# Solution: Check Tableau Desktop version compatibility
# Validate XML structure
# Check for duplicate UUIDs
```

---

This completes the MVP implementation guide. The system is now functional for basic bar chart generation with natural language interface!
