# File Structure Evaluation - CRITICAL ISSUE FOUND

## Current Structure (BROKEN)

```
TABLEAU-MCP/
├── src/                          ← Problem: src is a namespace package
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── schema_profiler.py
│   │   ├── xml_generator.py
│   │   └── uuid_utils.py
│   ├── llm/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── server.py
│   └── tableau_mcp/              ← Problem: Nested in src
│       ├── __init__.py
│       └── paths.py
├── setup.py
├── MANIFEST.in
└── requirements.txt
```

## The Problems

### Problem 1: Imports Use `src.` Prefix

**In server.py (line 6-11)**:
```python
from src.core.schema_profiler import SchemaProfiler      # ❌ Wrong
from src.core.xml_generator import TableauXMLCompiler    # ❌ Wrong
from src.llm.client import LLMClient                     # ❌ Wrong
from src.tableau_mcp.paths import get_output_dir         # ❌ Wrong
```

**Why it's wrong**:
- When user `pip install tableau-mcp-server`, the package name is `tableau_mcp`
- `src.` won't exist after pip install
- Users will get: `ModuleNotFoundError: No module named 'src'`

### Problem 2: Package Discovery is Wrong

**In setup.py**:
```python
packages=find_packages()
```

**What it finds**:
```
src
src.core
src.llm
src.mcp
src.tableau_mcp
```

**But you want**:
```
tableau_mcp
tableau_mcp.core
tableau_mcp.llm
tableau_mcp.mcp
```

### Problem 3: MANIFEST.in Uses Wrong Path

**Current**:
```
recursive-include src/tableau_mcp/templates *.twb
```

**But after fix, should be**:
```
recursive-include tableau_mcp/templates *.twb
```

---

## The Solution

You have **2 options**. I recommend **Option 1**.

---

## Option 1: Move Code Out of src/ (RECOMMENDED)

### New Structure
```
TABLEAU-MCP/
├── tableau_mcp/                  ✅ Direct package name
│   ├── __init__.py
│   ├── server.py
│   ├── paths.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── schema_profiler.py
│   │   ├── xml_generator.py
│   │   └── uuid_utils.py
│   ├── llm/
│   │   ├── __init__.py
│   │   └── client.py
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── server.py
│   └── templates/
│       └── base_template.twb
├── setup.py
├── MANIFEST.in
└── requirements.txt
```

### Changes Needed

#### Step 1: Rename Directory
```bash
cd /Users/kartik.arora/TABLEAU-MCP
mv src/tableau_mcp tableau_mcp
# Move other packages into tableau_mcp
mv src/core tableau_mcp/
mv src/llm tableau_mcp/
mv src/mcp tableau_mcp/
# Remove empty src
rmdir src
```

#### Step 2: Update Imports in server.py

**Before**:
```python
from src.core.schema_profiler import SchemaProfiler
from src.core.xml_generator import TableauXMLCompiler
from src.llm.client import LLMClient
from src.tableau_mcp.paths import get_output_dir, get_template_path
```

**After**:
```python
from tableau_mcp.core.schema_profiler import SchemaProfiler
from tableau_mcp.core.xml_generator import TableauXMLCompiler
from tableau_mcp.llm.client import LLMClient
from tableau_mcp.paths import get_output_dir, get_template_path
```

#### Step 3: Update setup.py

**Before**:
```python
packages=find_packages()
```

**After**:
```python
packages=find_packages()
# Now find_packages() will correctly find:
# - tableau_mcp
# - tableau_mcp.core
# - tableau_mcp.llm
# - tableau_mcp.mcp
```

#### Step 4: Update MANIFEST.in

**Before**:
```
recursive-include src/tableau_mcp/templates *.twb
```

**After**:
```
recursive-include tableau_mcp/templates *.twb
```

#### Step 5: Update ALL Imports Throughout Project

Check all Python files for imports:
```bash
cd /Users/kartik.arora/TABLEAU-MCP
grep -r "from src\." --include="*.py" .
grep -r "import src\." --include="*.py" .
```

Replace all `from src.` with `from tableau_mcp.`

---

## Option 2: Use src-Layout (Alternative)

### New Structure
```
TABLEAU-MCP/
├── src/
│   └── tableau_mcp/              ✅ src is just a container
│       ├── __init__.py
│       ├── server.py
│       ├── paths.py
│       ├── core/
│       ├── llm/
│       ├── mcp/
│       └── templates/
├── setup.py
├── MANIFEST.in
└── requirements.txt
```

### Changes Needed

#### Step 1: Restructure
```bash
cd /Users/kartik.arora/TABLEAU-MCP
# Move core, llm, mcp into tableau_mcp
mv src/core src/tableau_mcp/
mv src/llm src/tableau_mcp/
mv src/mcp src/tableau_mcp/
# Remove empty src folder and recreate
rm -rf src
mkdir -p src/tableau_mcp/templates
# Move tableau_mcp content into src/tableau_mcp/
```

#### Step 2: Update setup.py

```python
# Add where='src' to find_packages
packages=find_packages(where='src')
package_dir={'': 'src'}

package_data={
    'tableau_mcp': ['templates/*.twb'],
},
```

#### Step 3: Update Imports

Same as Option 1: Change `from src.` to `from tableau_mcp.`

#### Step 4: Update MANIFEST.in

Same as Option 1

---

## Comparison

| Aspect | Option 1 | Option 2 |
|--------|----------|----------|
| **Structure** | tableau_mcp at root | tableau_mcp in src/ |
| **Complexity** | Simple | Medium |
| **Standard** | Most common | PEP 517 standard |
| **setup.py** | `find_packages()` | `find_packages(where='src')` |
| **File moves** | 3 moves | 3 moves |
| **Import changes** | Remove src.` prefix | Remove `src.` prefix |
| **Recommended** | ✅ YES | If you prefer src-layout |

---

## Why This Matters

### Current Issue (Broken After pip install)
```bash
pip install tableau-mcp-server

python -c "from tableau_mcp import server"
# Error: ModuleNotFoundError: No module named 'src'
# Because imports say: from src.core...
# But after pip install, there is no src.
```

### After Fix (Works After pip install)
```bash
pip install tableau-mcp-server

python -c "from tableau_mcp import server"
# ✅ Works! Server starts without errors
```

---

## Step-by-Step Fix (Option 1 - Recommended)

### Step 1: Check Current Structure
```bash
cd /Users/kartik.arora/TABLEAU-MCP
find . -type f -name "*.py" | grep -E "(src|tableau_mcp)" | head -20
```

### Step 2: Backup (Safety First!)
```bash
cd /Users/kartik.arora/TABLEAU-MCP
git add -A
git commit -m "Backup before structure refactor"
```

### Step 3: Restructure
```bash
# Rename src folder to tableau_mcp at root
mv src/tableau_mcp tableau_mcp_temp
cd src
# Move all packages
mv core ../
mv llm ../
mv mcp ../
cd ..
# Remove src directory
rm -rf src
# Restore tableau_mcp folder
mv tableau_mcp_temp/paths.py tableau_mcp_temp/__init__.py tableau_mcp/
rmdir tableau_mcp_temp
```

Result:
```
TABLEAU-MCP/
├── tableau_mcp/
│   ├── __init__.py
│   ├── server.py
│   ├── paths.py
│   ├── core/
│   ├── llm/
│   ├── mcp/
│   └── templates/
├── setup.py
```

### Step 4: Update All Imports

Find all files with `src.` imports:
```bash
grep -r "from src\." --include="*.py" . | cut -d: -f1 | sort -u
```

For each file, replace:
- `from src.core` → `from tableau_mcp.core`
- `from src.llm` → `from tableau_mcp.llm`
- `from src.mcp` → `from tableau_mcp.mcp`
- `from src.tableau_mcp` → `from tableau_mcp`

### Step 5: Update setup.py
```python
# Keep as is:
packages=find_packages()

# Update package_data to match new path:
package_data={
    'tableau_mcp': ['templates/*.twb'],
},
```

### Step 6: Update MANIFEST.in
```
recursive-include tableau_mcp/templates *.twb
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
include README.md
include LICENSE
include .env.example
```

### Step 7: Test
```bash
python -m build
python -c "from tableau_mcp import server; print('✅ Success')"
```

---

## Why This Was Confusing

Your structure had:
- **src/** = namespace package (not meant to be shipped)
- **src/core/, src/llm/, src/mcp/** = subpackages (shipped)
- **src/tableau_mcp/** = confusing nesting

This works during development because Python finds `src/` locally. But after `pip install`:
- `src/` folder doesn't exist
- Imports fail
- Package can't be used

---

## Best Practice Going Forward

### Standard Python Package Structure

```
package-name/                   (GitHub repo name)
├── package_name/               (Python package, matches pip name)
│   ├── __init__.py
│   ├── core/
│   ├── utils/
│   ├── models/
│   └── data/
├── tests/                       (Not packaged)
├── examples/                    (Optional)
├── docs/                        (Optional)
├── setup.py
├── MANIFEST.in
├── requirements.txt
├── README.md
└── LICENSE
```

Your package name = `tableau_mcp`  
Your folder name = `tableau_mcp/`  
NOT nested in `src/`

---

## Summary

| Issue | Current | Fixed |
|-------|---------|-------|
| **Imports** | `from src.core...` | `from tableau_mcp.core...` |
| **Package location** | src/tableau_mcp/ | tableau_mcp/ |
| **After pip install** | ❌ Breaks | ✅ Works |
| **Time to fix** | — | 20 minutes |

---

## Next Action

**Choose one**:
- [ ] **Option 1** (Recommended): Restructure out of src/
- [ ] **Option 2** (Alternative): Keep src-layout style

Once you choose, I'll provide exact commands to fix it!
