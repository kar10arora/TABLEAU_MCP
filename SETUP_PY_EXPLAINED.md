# setup.py & MANIFEST.in Explained

## What They Do

`setup.py` = "How to package and install this Python project"  
`MANIFEST.in` = "What data files (non-Python) to include in the package"

---

## The 2 Critical Lines Added to setup.py

### Line 1: `include_package_data=True`

```python
include_package_data=True,
```

**What it does**: Tells pip "Look at MANIFEST.in and include those files in the package"

**Why it's needed**: Without this, pip ignores MANIFEST.in and only includes Python code files (.py)

**Result**: When someone `pip install tableau-mcp-server`, the template file gets included

---

### Line 2: `package_data` Dictionary

```python
package_data={
    'tableau_mcp': ['templates/*.twb'],
},
```

**What it does**: Explicitly tells pip which non-Python files to include

**Why it's needed**: Fallback in case MANIFEST.in doesn't work (some edge cases)

**Breakdown**:
- `'tableau_mcp'` = the package name containing the files
- `'templates/*.twb'` = "include all .twb files from the templates folder"

---

## Your Updated setup.py

### BEFORE (Missing Template Packaging)
```python
setup(
    name="tableau-mcp-server",
    version="1.0.0",
    author="Tableau MCP Team",
    ...
    packages=find_packages(),
    # ❌ NO include_package_data
    # ❌ NO package_data
    classifiers=[
        ...
    ],
)

# Problem: When pip installs, template file is NOT included!
# User gets: ModuleNotFoundError: Template not found
```

### AFTER (Correctly Packages Template)
```python
setup(
    name="tableau-mcp-server",
    version="1.0.0",
    author="Tableau MCP Team",
    ...
    packages=find_packages(),
    include_package_data=True,  # ✅ READ MANIFEST.in
    package_data={  # ✅ INCLUDE TEMPLATES
        'tableau_mcp': ['templates/*.twb'],
    },
    classifiers=[
        ...
    ],
)

# Result: When pip installs, template is automatically included!
# User gets: Works perfectly, no configuration needed
```

---

## Your MANIFEST.in Explained

### Line 1: Include Template Files
```
recursive-include src/tableau_mcp/templates *.twb
```
- `recursive-include` = Look in this folder AND all subfolders
- `src/tableau_mcp/templates` = Path to template folder
- `*.twb` = Include all Tableau workbook files

**Result**: `base_template.twb` gets packaged

### Line 2-3: Exclude Python Cache Files
```
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
```
- Don't include compiled Python files (pyc, pyo)
- These shouldn't be in the package (created during runtime)

### Line 4-6: Include Documentation
```
include README.md
include LICENSE
include .env.example
```
- Include these files in the package
- Good practice for distribution

---

## How It All Works Together

```
Your Project Structure
├── src/
│   └── tableau_mcp/
│       ├── __init__.py
│       ├── server.py
│       ├── paths.py
│       ├── core/
│       │   ├── schema_profiler.py
│       │   └── xml_generator.py
│       └── templates/
│           └── base_template.twb  ← This file gets packaged!
│
├── MANIFEST.in  ← Tells pip what to include
└── setup.py     ← Tells pip HOW to package

When user runs: pip install tableau-mcp-server

Step 1: setup.py is read
  ├─ Finds all packages (find_packages())
  ├─ Reads MANIFEST.in (include_package_data=True)
  └─ Includes package_data

Step 2: MANIFEST.in is processed
  ├─ Finds src/tableau_mcp/templates/*.twb
  └─ Adds base_template.twb to package

Step 3: Wheel/sdist is created with everything
  └─ When installed, template is in site-packages

Step 4: User's paths.py finds it
  ├─ importlib.resources.files('tableau_mcp')
  └─ Returns: ~/.venv/lib/python3.x/site-packages/tableau_mcp/templates/base_template.twb

Result: Works perfectly! ✅
```

---

## Testing It Works

### Step 1: Build the Package
```bash
cd /Users/kartik.arora/TABLEAU-MCP
pip install build
python -m build
```

**What this creates**:
- `dist/tableau-mcp-server-1.0.0.tar.gz` (source distribution)
- `dist/tableau-mcp-server-1.0.0-py3-none-any.whl` (wheel - binary)

**Inside the wheel, you should see**:
```
tableau_mcp/
├── server.py
├── paths.py
├── templates/
│   └── base_template.twb  ✅ IS INCLUDED
└── ... other files
```

### Step 2: Test Installation in Clean Environment
```bash
# Create clean Python environment
python -m venv /tmp/test_tableau_env
source /tmp/test_tableau_env/bin/activate

# Install your package
pip install /Users/kartik.arora/TABLEAU-MCP/dist/tableau-mcp-server-1.0.0-py3-none-any.whl

# TEST 1: Import works
python -c "from tableau_mcp import server; print('✅ Import OK')"

# TEST 2: Template is found
python -c "from tableau_mcp.paths import get_template_path; t = get_template_path(); print(f'✅ Template: {t}')"

# TEST 3: Output dir auto-created
python -c "from tableau_mcp.paths import get_output_dir; d = get_output_dir(); print(f'✅ Output: {d}')"

# TEST 4: Server starts
python -m tableau_mcp.server
# Should output: INFO: Started server process...
```

---

## If Template Doesn't Get Packaged

**Symptoms**:
```
FileNotFoundError: Template 'base_template.twb' not found
```

**Fixes in order**:

1. ✅ Check `include_package_data=True` is in setup.py
2. ✅ Check MANIFEST.in exists and is correct
3. ✅ Rebuild: `python -m build --force-all`
4. ✅ Reinstall in clean venv

---

## What Happens When User Installs

User runs:
```bash
pip install tableau-mcp-server
```

Pip does:
1. ✅ Downloads package from PyPI (or GitHub)
2. ✅ Reads setup.py (finds include_package_data=True)
3. ✅ Reads MANIFEST.in (includes templates/*.twb)
4. ✅ Extracts to site-packages/tableau_mcp/
5. ✅ Template automatically in correct location
6. ✅ User's paths.py finds it automatically

User configures:
```json
{
  "mcpServers": {
    "tableau-generator": {
      "command": "python",
      "args": ["-m", "tableau_mcp.server"],
      "env": {"GEMINI_API_KEY": "sk-..."}
    }
  }
}
```

No paths to change, no directories to create, template is auto-found! ✅

---

## Summary

| Component | Purpose | What It Does |
|-----------|---------|--------------|
| **setup.py** | Package config | Tells pip how to install |
| **include_package_data=True** | Enable MANIFEST.in | Reads what files to include |
| **package_data** | Fallback inclusion | Explicitly list data files |
| **MANIFEST.in** | Data file list | "Include templates, README, etc" |
| **paths.py** | Smart resolution | Finds template wherever installed |

**Result**: Distributable, pip-installable MCP that works anywhere 🚀

---

## Key Points to Remember

✅ **MANIFEST.in** tells pip WHAT to include  
✅ **setup.py** tells pip HOW to package  
✅ **include_package_data=True** enables MANIFEST.in  
✅ **package_data** provides fallback  
✅ **paths.py** finds files at runtime  

All 5 together = **Distribution-ready MCP**
