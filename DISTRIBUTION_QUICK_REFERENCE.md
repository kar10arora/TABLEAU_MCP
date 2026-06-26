# Tableau MCP Distribution - Quick Reference Card

## TL;DR: What Needs to Change

Your MCP works for **you** but **not for others** because:
- ❌ Paths are hardcoded to `/Users/kartik.arora/TABLEAU-MCP/`
- ❌ Template file isn't packaged with pip install
- ❌ Users must manually configure absolute paths

**Solution**: Smart path resolution + proper packaging

---

## 4 Files to Create/Modify

### 1️⃣ CREATE: `src/tableau_mcp/paths.py` (50 lines)
Purpose: Smart path resolution that works anywhere

```python
import importlib.resources as resources
from pathlib import Path
import os

def get_template_path() -> str:
    """Find template whether installed or in dev."""
    try:
        if hasattr(resources, 'files'):
            return str(resources.files('tableau_mcp').joinpath(
                'templates', 'base_template.twb'
            ))
    except:
        pass
    
    dev_path = Path(__file__).parent.parent / 'templates' / 'base_template.twb'
    if dev_path.exists():
        return str(dev_path)
    
    raise FileNotFoundError(
        "Install with: pip install tableau-mcp-server"
    )

def get_output_dir(create: bool = True) -> str:
    """Get output dir (default: ~/.tableau-mcp/workbooks)."""
    if env_dir := os.getenv("TABLEAU_OUTPUT_DIR"):
        output_path = Path(env_dir)
    else:
        output_path = Path.home() / '.tableau-mcp' / 'workbooks'
    
    if create:
        output_path.mkdir(parents=True, exist_ok=True)
    
    return str(output_path)
```

### 2️⃣ MODIFY: `src/mcp/server.py` (2 changes)
Replace lines 19 and 66:

**OLD**:
```python
TEMPLATE_PATH = os.getenv("TEMPLATE_DIR", "./templates") + "/base_template.twb"
...
output_dir = os.getenv("OUTPUT_DIR", "./examples/generated_workbooks")
```

**NEW**:
```python
from src.tableau_mcp.paths import get_template_path, get_output_dir

TEMPLATE_PATH = get_template_path()
DEFAULT_OUTPUT_DIR = get_output_dir(create=True)
...
output_path = os.path.join(DEFAULT_OUTPUT_DIR, "generated_workbook.twb")
```

### 3️⃣ CREATE: `MANIFEST.in` (3 lines)
Purpose: Tell pip to include template file

```
recursive-include src/tableau_mcp/templates *.twb
recursive-exclude * __pycache__
```

### 4️⃣ MODIFY: `setup.py` (Full replacement)
Add these key lines:

```python
setup(
    name="tableau-mcp-server",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,  # ← ADD THIS
    package_data={  # ← ADD THIS
        'tableau_mcp': ['templates/*.twb'],
    },
    # ... rest of config
)
```

---

## 5-Minute Test After Changes

```bash
cd /Users/kartik.arora/TABLEAU-MCP

# 1. Build package
pip install build
python -m build

# 2. Test in clean environment
python -m venv /tmp/test_tableau_env
source /tmp/test_tableau_env/bin/activate

# 3. Install from your build
pip install dist/tableau-mcp-server-1.0.0-py3-none-any.whl

# 4. Verify template is found (should NOT error)
python -c "from tableau_mcp.paths import get_template_path; print(get_template_path())"

# 5. Verify server starts
python -m tableau_mcp.server
```

---

## Result: User Experience

### Before (Your Current Setup)
```json
{
  "mcpServers": {
    "tableau-generator": {
      "command": "python",
      "args": ["/Users/kartik.arora/TABLEAU-MCP/src/mcp/server.py"],
      "env": {
        "TEMPLATE_DIR": "/Users/kartik.arora/TABLEAU-MCP/templates",
        "OUTPUT_DIR": "/Users/kartik.arora/TABLEAU-MCP/examples/generated_workbooks"
      }
    }
  }
}
```
❌ Other users must change ALL paths  
❌ Breaks immediately  
❌ Can't distribute

### After (Distribution-Ready)
```json
{
  "mcpServers": {
    "tableau-generator": {
      "command": "python",
      "args": ["-m", "tableau_mcp.server"],
      "env": {
        "GEMINI_API_KEY": "sk-..."
      }
    }
  }
}
```
✅ Same for all users  
✅ Works immediately  
✅ Ready for PyPI/distribution

---

## User Installation (After Your Changes)

```bash
# User just needs:
pip install tableau-mcp-server

# Add API key to ~/.env
GEMINI_API_KEY=sk-...

# Add to ~/.claude/settings.json (copy-paste)
# Done! No path configuration needed
```

---

## Distribution Timeline

| When | What | Time |
|------|------|------|
| **Now** | Create paths.py + modify 3 files | 30 min |
| **Now** | Test build & installation | 20 min |
| **Later** | Push to GitHub | 5 min |
| **Later** | (Optional) Publish to PyPI | 10 min |

**Total effort**: 1-2 hours to become **distribution-ready**

---

## Checklist

### Code Changes
- [ ] Create `src/tableau_mcp/paths.py`
- [ ] Update `src/mcp/server.py` (2 lines)
- [ ] Create `MANIFEST.in`
- [ ] Update `setup.py`

### Testing
- [ ] `python -m build` succeeds
- [ ] `pip install` works in clean venv
- [ ] Template auto-found
- [ ] Server starts without errors
- [ ] No hardcoded paths in output

### Distribution
- [ ] Push to GitHub
- [ ] (Optional) Publish to PyPI
- [ ] Users can `pip install` without path config

---

## Common Questions Answered

**Q: Will existing users' configs break?**  
A: Yes, they need to update. But new config is simpler (no paths).

**Q: What if user wants custom output directory?**  
A: They set `TABLEAU_OUTPUT_DIR` env var (optional).

**Q: Does pip install copy template file?**  
A: Yes, `MANIFEST.in` + `include_package_data=True` handles it.

**Q: How do users get `paths.py`?**  
A: It's part of the package, installed automatically.

**Q: What Python versions needed?**  
A: 3.9+ (for `importlib.resources`)

---

## Files You'll Create/Modify

```
TABLEAU-MCP/
├── src/tableau_mcp/
│   ├── paths.py              ← CREATE (50 lines)
│   └── mcp/
│       └── server.py         ← MODIFY (2 changes)
│
├── setup.py                  ← MODIFY (add 3 lines)
├── MANIFEST.in               ← CREATE (3 lines)
└── pyproject.toml            ← CREATE (optional, 25 lines)
```

**Total changes**: ~100 lines of code  
**Complexity**: Low (mostly config, not logic)  
**Impact**: Makes MCP distributable to anyone

---

## What Happens After

✅ Users can: `pip install tableau-mcp-server`  
✅ Users can: Use without path configuration  
✅ Users can: Works on any system  
✅ You can: Publish to PyPI  
✅ You can: Distribute via GitHub  
✅ Community can: Use professionally

---

**Key Insight**: Right now your MCP is like building a car but only leaving it in your garage. Distribution-ready means anyone can pick it up and drive it. 🚗
