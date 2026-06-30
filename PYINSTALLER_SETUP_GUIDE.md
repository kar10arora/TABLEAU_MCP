# PyInstaller Setup - Option 3 Complete Guide

## Status: ✅ READY FOR PYINSTALLER

Your file structure is already compatible with PyInstaller.

---

## What Is PyInstaller?

PyInstaller converts Python code into a **standalone executable binary** that:
- ✅ Users can run directly
- ✅ Hides all source code
- ✅ No Python installation needed by user
- ✅ Works on any OS (Windows, Mac, Linux)

**User won't see your code** - only the compiled binary.

---

## Current Structure Status

```
✅ tableau_mcp/              - Package ready
   ├── ✅ core/
   ├── ✅ llm/
   ├── ✅ mcp/
   │   └── ✅ server.py (has if __name__ == "__main__")
   ├── ✅ paths.py
   └── ✅ templates/

✅ setup.py                 - Ready for distribution
✅ MANIFEST.in             - Correct configuration
✅ All imports             - Using tableau_mcp.* prefix

Ready to build binary! 🎯
```

---

## E2E Setup Steps (45 minutes)

### PHASE 1: Create Entry Point (5 minutes)

#### Step 1.1: Create `tableau_mcp/__main__.py`

This file makes your package runnable as `python -m tableau_mcp`:

```python
"""
Entry point for running tableau_mcp as a module.
This is what PyInstaller will compile.
"""

from tableau_mcp.mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
```

Create the file:
```bash
cat > /Users/kartik.arora/TABLEAU-MCP/tableau_mcp/__main__.py << 'EOF'
"""
Entry point for running tableau_mcp as a module.
This is what PyInstaller will compile.
"""

from tableau_mcp.mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
EOF
```

#### Step 1.2: Verify It Works

```bash
python -m tableau_mcp
# Should output: MCP server starting...
```

---

### PHASE 2: Install PyInstaller (2 minutes)

```bash
pip install pyinstaller==6.10.0
```

**Verify installation**:
```bash
pyinstaller --version
# Should output: 6.10.0
```

---

### PHASE 3: Create Binary (20 minutes)

#### Step 3.1: Build the Executable

```bash
cd /Users/kartik.arora/TABLEAU-MCP

# Build single-file executable
pyinstaller \
  --onefile \
  --name tableau-mcp \
  --icon=NONE \
  --hidden-import=fastmcp \
  --hidden-import=pandas \
  --hidden-import=lxml \
  --hidden-import=google.generativeai \
  --hidden-import=openai \
  --hidden-import=dotenv \
  -p tableau_mcp \
  tableau_mcp/__main__.py
```

**What this does**:
- `--onefile`: Creates single executable (not a folder)
- `--name tableau-mcp`: Names the executable
- `--hidden-import`: Includes dependencies PyInstaller might miss
- `-p tableau_mcp`: Adds package to path

#### Step 3.2: Watch the Build

```
Output will show:
69 INFO: PyInstaller: 6.10.0
70 INFO: Python: 3.12.13
...
1234 INFO: Building EXE from EXE-00.toc completed successfully.
```

**This takes 15-20 minutes** (first time is slower)

#### Step 3.3: Find the Binary

```bash
# The executable is here:
ls -lh dist/tableau-mcp

# Example output:
# -rwxr-xr-x  45M tableau-mcp  (45MB executable - this is normal)
```

---

### PHASE 4: Test the Binary (10 minutes)

#### Step 4.1: Test in Clean Environment

```bash
# Create test directory
mkdir -p /tmp/test_tableau_mcp
cd /tmp/test_tableau_mcp

# Copy the binary
cp /Users/kartik.arora/TABLEAU-MCP/dist/tableau-mcp .

# Set executable permission
chmod +x tableau-mcp

# Test it runs
./tableau-mcp
# Should output: MCP server starting...
# Should NOT show any Python code or errors
```

#### Step 4.2: Verify Code is Hidden

```bash
# Try to read the binary
strings dist/tableau-mcp | grep "schema_profiler"
# Should output nothing (code is compiled, not visible)

# Try to extract code
file dist/tableau-mcp
# Should show: ELF 64-bit executable (on Linux)
# or Mach-O 64-bit executable (on Mac)
```

#### Step 4.3: Check Binary Size

```bash
du -h dist/tableau-mcp
# Expected: 40-50 MB (dependencies included)
```

---

### PHASE 5: Update Setup.py (5 minutes)

#### Step 5.1: Add Binary to setup.py

Update `setup.py` to include the binary in the package:

```python
# In setup.py, update the setup() call to include:

setup(
    name="tableau-mcp-server",
    version="1.0.0",
    ...
    
    # Add this section:
    package_data={
        'tableau_mcp': [
            'templates/*.twb',
        ],
    },
    
    # Add this section (NEW):
    data_files=[
        ('bin', ['dist/tableau-mcp']),  # Include the binary
    ],
    
    # Add entry point to make it work:
    entry_points={
        'console_scripts': [
            'tableau-mcp=tableau_mcp.mcp.server:mcp.run',
        ],
    },
    
    ...
)
```

---

### PHASE 6: Package for Distribution (3 minutes)

#### Step 6.1: Build the Distribution Package

```bash
python -m build
```

**This creates**:
- `dist/tableau-mcp-server-1.0.0.tar.gz` (source)
- `dist/tableau-mcp-server-1.0.0-py3-none-any.whl` (wheel)

#### Step 6.2: Include the Binary

For pip distribution, you have options:

**Option A: Include Binary in Wheel**
```bash
# The wheel includes the binary from dist/
# Users get: tableau-mcp command automatically
```

**Option B: Distribute Binary Separately**
```bash
# Create a separate release with:
# - tableau-mcp (the binary)
# Users download and run it directly
```

---

## Complete Command Sequence (Copy-Paste Ready)

```bash
#!/bin/bash
# Run this to build everything from scratch

cd /Users/kartik.arora/TABLEAU-MCP

echo "1️⃣  Installing PyInstaller..."
pip install pyinstaller==6.10.0

echo "2️⃣  Creating entry point..."
cat > tableau_mcp/__main__.py << 'EOF'
"""Entry point for running tableau_mcp as a module."""
from tableau_mcp.mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
EOF

echo "3️⃣  Testing module runs..."
python -m tableau_mcp &
sleep 2
kill %1 2>/dev/null

echo "4️⃣  Building executable with PyInstaller..."
pyinstaller \
  --onefile \
  --name tableau-mcp \
  --icon=NONE \
  --hidden-import=fastmcp \
  --hidden-import=pandas \
  --hidden-import=lxml \
  --hidden-import=google.generativeai \
  --hidden-import=openai \
  --hidden-import=dotenv \
  -p tableau_mcp \
  tableau_mcp/__main__.py

echo "5️⃣  Verifying binary..."
ls -lh dist/tableau-mcp
chmod +x dist/tableau-mcp

echo "6️⃣  Testing binary in isolation..."
# Copy to temp and test
cp dist/tableau-mcp /tmp/tableau-mcp-test
/tmp/tableau-mcp-test &
sleep 2
kill %1 2>/dev/null

echo "✅ DONE! Binary ready at: dist/tableau-mcp"
echo ""
echo "Next steps:"
echo "1. Commit: git add -A && git commit -m 'Add PyInstaller setup'"
echo "2. Test: ./dist/tableau-mcp"
echo "3. Release: Include dist/tableau-mcp in your release"
```

---

## User Experience After Distribution

### Without PyInstaller (Option 1/2)
```bash
pip install tableau-mcp-server
# User gets Python package + source code (visible)

python -m tableau_mcp.server
# Or: tableau-mcp (if using entry points)
```

### With PyInstaller (Option 3) ✅
```bash
pip install tableau-mcp-server
# User gets binary executable + data files

tableau-mcp
# User runs the compiled binary
# NO SOURCE CODE VISIBLE
```

---

## File Structure After PyInstaller Setup

```
TABLEAU-MCP/
├── tableau_mcp/
│   ├── __main__.py          ✅ NEW - Entry point for PyInstaller
│   ├── server.py
│   ├── paths.py
│   ├── core/
│   ├── llm/
│   ├── mcp/
│   └── templates/
│
├── dist/
│   ├── tableau-mcp          ✅ COMPILED BINARY (45MB)
│   ├── tableau-mcp-server-1.0.0.tar.gz
│   └── tableau-mcp-server-1.0.0-py3-none-any.whl
│
├── build/                   (PyInstaller build artifacts)
├── tableau-mcp.spec         (PyInstaller spec file)
└── setup.py
```

---

## Verification Checklist

### ✅ Before Building

- [ ] `tableau_mcp/__main__.py` exists
- [ ] `python -m tableau_mcp` runs without errors
- [ ] All imports use `tableau_mcp.*` prefix
- [ ] `setup.py` has correct configuration
- [ ] PyInstaller is installed

### ✅ After Building

- [ ] `dist/tableau-mcp` exists and is executable
- [ ] Binary runs: `./dist/tableau-mcp`
- [ ] No Python files in binary (not readable with strings)
- [ ] Binary size is 40-50 MB (expected)

### ✅ After Packaging

- [ ] `dist/tableau-mcp-server-1.0.0.whl` exists
- [ ] Package includes binary
- [ ] Can install with pip

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'X'"

**Solution**: Add to PyInstaller command:
```bash
--hidden-import=module_name
```

Example:
```bash
pyinstaller \
  --onefile \
  --hidden-import=fastmcp \
  --hidden-import=your_module \
  tableau_mcp/__main__.py
```

### "Binary is too large (100+ MB)"

This is **normal and expected**. All dependencies are included.

To reduce size:
```bash
pyinstaller \
  --onefile \
  --strip \  # Strip debug symbols
  --upx-dir=/path/to/upx \  # UPX compression
  tableau_mcp/__main__.py
```

### "Binary doesn't work when copied to another folder"

This can happen with data files. Solution:

Use `get_template_path()` in paths.py which handles this:
```python
# paths.py already does this correctly ✅
def get_template_path() -> str:
    """Find template in compiled binary or dev environment."""
    # Handles both cases
```

### "Users can still see imports in binary"

This is **normal**. Import statements are necessary for runtime.

To truly hide: Use Cython (more complex, not recommended).

---

## What Users See (The Key Benefit)

### User Downloads tableau-mcp Binary

```bash
# User's system
$ ls -la
-rwxr-xr-x  45M  tableau-mcp

$ file tableau-mcp
tableau-mcp: ELF 64-bit executable

# User tries to read code
$ cat tableau-mcp | head
# Binary garbage - not readable!

# User just runs it
$ ./tableau-mcp
✅ MCP server running
```

### User Never Sees Python Files

✅ No `schema_profiler.py`  
✅ No `xml_generator.py`  
✅ No `llm/client.py`  
✅ No implementation details  
✅ No source code to modify  

---

## Timeline

| Phase | Task | Time |
|-------|------|------|
| **1** | Create __main__.py | 2 min |
| **2** | Install PyInstaller | 1 min |
| **3** | Build executable | 20 min |
| **4** | Test binary | 5 min |
| **5** | Update setup.py | 3 min |
| **6** | Package distribution | 3 min |
| **Total** | | **34 min** |

---

## Distribution Methods

### Option A: Binary-Only Release
```bash
# Release just the binary
tableau-mcp (45MB executable)

# Users run it directly
./tableau-mcp
```

### Option B: pip Install with Binary
```bash
# pip includes the binary
pip install tableau-mcp-server

# Users run it
tableau-mcp
```

### Option C: Both (Recommended)
```bash
# Release both:
1. tableau-mcp (binary) - for direct use
2. tableau-mcp-server (pip) - for managed installation

# Users choose:
# Direct: Download and run binary
# Or: pip install tableau-mcp-server
```

---

## Why Use PyInstaller (Option 3)?

✅ **Code Protection**: Source code is compiled, not visible  
✅ **No Python Needed**: Users don't need Python installed  
✅ **Enterprise**: Professional distribution  
✅ **Single File**: Easy to share and deploy  
✅ **Cross-Platform**: Build once, works everywhere  

---

## Next Actions

### Immediate (Do Now)
1. Create `tableau_mcp/__main__.py`
2. Install PyInstaller
3. Build the binary
4. Test it works

### Then (After Testing)
1. Update setup.py
2. Build distribution package
3. Commit changes
4. Push to GitHub
5. Create release with binary

---

## Copy-Paste: Quick Start (All-In-One)

```bash
#!/bin/bash
set -e

PROJECT="/Users/kartik.arora/TABLEAU-MCP"
cd "$PROJECT"

echo "🔨 PYINSTALLER SETUP"
echo "===================="

# 1. Create entry point
echo "📝 Creating __main__.py..."
cat > tableau_mcp/__main__.py << 'EOF'
"""Entry point for tableau_mcp."""
from tableau_mcp.mcp.server import mcp
if __name__ == "__main__":
    mcp.run()
EOF

# 2. Install PyInstaller
echo "📦 Installing PyInstaller..."
pip install -q pyinstaller==6.10.0

# 3. Build binary
echo "🔨 Building executable (this takes ~20 minutes)..."
pyinstaller \
  --onefile \
  --name tableau-mcp \
  --hidden-import=fastmcp \
  --hidden-import=pandas \
  --hidden-import=lxml \
  --hidden-import=google.generativeai \
  --hidden-import=openai \
  --hidden-import=dotenv \
  -p tableau_mcp \
  tableau_mcp/__main__.py 2>&1 | grep -E "(INFO|completed|error)"

# 4. Make executable
echo "🔧 Making executable..."
chmod +x dist/tableau-mcp

# 5. Verify
echo "✅ Verifying..."
ls -lh dist/tableau-mcp
file dist/tableau-mcp

echo ""
echo "🎉 SUCCESS!"
echo "Binary ready at: $PROJECT/dist/tableau-mcp"
echo ""
echo "Test it:"
echo "  ./dist/tableau-mcp"
```

Save as `build.sh`, then run:
```bash
chmod +x build.sh
./build.sh
```

---

## Status: Ready to Build! 🚀

Your code is **fully prepared** for PyInstaller.

Next: Run the build commands above to create your binary!
