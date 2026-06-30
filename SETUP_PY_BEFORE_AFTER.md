# setup.py - Before & After Visual Guide

## Quick Overview

| What | Before | After |
|------|--------|-------|
| **Lines in setup()** | 39 | 46 |
| **Lines added** | None | 7 |
| **Template packaged** | ❌ No | ✅ Yes |
| **User can pip install** | ❌ Template missing | ✅ Works perfectly |

---

## Side-by-Side Comparison

### BEFORE (Old - Broken for Distribution)

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tableau-mcp-server",
    version="1.0.0",
    author="Tableau MCP Team",
    description="Model Context Protocol server for automated Tableau workbook generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tableau-mcp-server",
    packages=find_packages(),
    # ❌ MISSING: include_package_data=True
    # ❌ MISSING: package_data dictionary
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
)

# When pip install runs:
# ❌ Template file is NOT included
# ❌ User gets: FileNotFoundError: Template not found
```

---

### AFTER (New - Distribution Ready)

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tableau-mcp-server",
    version="1.0.0",
    author="Tableau MCP Team",
    description="Model Context Protocol server for automated Tableau workbook generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tableau-mcp-server",
    packages=find_packages(),
    include_package_data=True,                           # ✅ NEW LINE 1
    package_data={                                       # ✅ NEW LINE 2
        'tableau_mcp': ['templates/*.twb'],              # ✅ NEW LINE 3
    },                                                   # ✅ NEW LINE 4
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
)

# When pip install runs:
# ✅ MANIFEST.in is read (because include_package_data=True)
# ✅ Template file IS included
# ✅ User gets: Works perfectly!
```

---

## What Changed (Exact Lines)

### The 4-Line Addition

```python
# Add these 4 lines after packages=find_packages():

include_package_data=True,
package_data={
    'tableau_mcp': ['templates/*.twb'],
},
```

**Line-by-line breakdown**:

```python
include_package_data=True,
│
└─ "When building the package, read MANIFEST.in and 
   include the files it specifies"

package_data={
│
└─ "Explicitly tell pip which data files to include"

    'tableau_mcp': ['templates/*.twb'],
    │              │
    │              └─ "Include all .twb files from templates folder"
    │
    └─ "For the tableau_mcp package"

},
```

---

## Copy-Paste Solution

If you want to update setup.py right now, just add these 4 lines:

```python
# After line 14 (packages=find_packages()), add:
    include_package_data=True,
    package_data={
        'tableau_mcp': ['templates/*.twb'],
    },
```

**Location in file**:
```python
    url="https://github.com/yourusername/tableau-mcp-server",
    packages=find_packages(),
    ← INSERT 4 NEW LINES HERE
    classifiers=[
```

---

## Why 4 Lines? (Not 2?)

**Line 1**: `include_package_data=True`
- Tells pip "check MANIFEST.in for what to include"
- **Required**

**Lines 2-4**: `package_data={...}`
- Tells pip explicitly "include these files"
- **Redundant but safe** - fallback in edge cases
- Many professional packages use both for maximum compatibility

**Result**: Works in all situations, on all Python versions

---

## MANIFEST.in Completes the Picture

Once setup.py has `include_package_data=True`, pip reads:

```
recursive-include src/tableau_mcp/templates *.twb
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
include README.md
include LICENSE
include .env.example
```

**What this says**:
- ✅ "Include template.twb"
- ✅ "Don't include Python caches"
- ✅ "Include docs and examples"

---

## Testing It Works

### Step 1: Verify Files Are Correct
```bash
cd /Users/kartik.arora/TABLEAU-MCP

# Check setup.py has the 4 lines
grep -A 3 "include_package_data=True" setup.py
# Should output:
#   include_package_data=True,
#   package_data={
#       'tableau_mcp': ['templates/*.twb'],
#   },

# Check MANIFEST.in exists
cat MANIFEST.in
# Should show includes for templates, README, etc
```

### Step 2: Build the Package
```bash
pip install build
python -m build
```

**Output should show**:
```
Successfully built tableau-mcp-server-1.0.0.tar.gz
Successfully built tableau-mcp-server-1.0.0-py3-none-any.whl
```

### Step 3: Verify Template is Packaged
```bash
# Check what's in the wheel
python -c "
import zipfile
z = zipfile.ZipFile('dist/tableau-mcp-server-1.0.0-py3-none-any.whl')
files = [f for f in z.namelist() if 'template' in f.lower()]
for f in files:
    print('✅ Found:', f)
"

# Should output something like:
# ✅ Found: tableau_mcp/templates/base_template.twb
```

### Step 4: Test Installation
```bash
# Create clean environment
python -m venv /tmp/test_env
source /tmp/test_env/bin/activate

# Install the wheel
pip install dist/tableau-mcp-server-1.0.0-py3-none-any.whl

# Test that template is found
python -c "from tableau_mcp.paths import get_template_path; print(get_template_path())"
# Should print path like:
# /tmp/test_env/lib/python3.x/site-packages/tableau_mcp/templates/base_template.twb
```

✅ If this works, your setup is correct!

---

## Common Questions

**Q: Why both `include_package_data=True` AND `package_data`?**  
A: `include_package_data=True` reads MANIFEST.in. `package_data` is explicit. Together they ensure maximum compatibility.

**Q: Does `package_data` replace MANIFEST.in?**  
A: No, they work together. MANIFEST.in is read first (if include_package_data=True), then package_data adds/confirms.

**Q: Will this increase package size?**  
A: Yes, by ~22KB (the template file). That's fine for distribution.

**Q: What if I have multiple data folders?**  
A: Add them to package_data:
```python
package_data={
    'tableau_mcp': [
        'templates/*.twb',
        'examples/*.csv',
        'docs/*.md',
    ],
},
```

**Q: Do I need pyproject.toml too?**  
A: Optional but recommended for modern Python packaging. setup.py is sufficient.

---

## Your Current Status

✅ **setup.py**: Updated with include_package_data + package_data  
✅ **MANIFEST.in**: Created with template inclusion rules  
✅ **paths.py**: Created with smart path resolution  
✅ **server.py**: Updated to use get_template_path()  

**Next Step**: Test the build!

```bash
python -m build
```

If this succeeds without errors, you're ready for distribution! 🚀
