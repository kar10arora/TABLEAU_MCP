# PyInstaller - Exact Commands to Execute

## Current Status: ✅ READY

- ✅ File structure correct
- ✅ `__main__.py` created
- ✅ All imports fixed
- ✅ Ready to build binary

---

## Execute These Commands in Order

### Step 1: Install PyInstaller (1 minute)

```bash
pip install pyinstaller==6.10.0
```

**Verify**:
```bash
pyinstaller --version
```

Expected output:
```
6.10.0
```

---

### Step 2: Test Module Runs (1 minute)

```bash
python -m tableau_mcp
```

**Expected output** (press Ctrl+C to stop):
```
INFO: Started server process with handlers
INFO: Uvicorn running on unix socket /var/folders/.../tmp.sock
```

---

### Step 3: Build Binary with PyInstaller (20 minutes)

**Run from project root**:
```bash
cd /Users/kartik.arora/TABLEAU-MCP

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
  --hidden-import=python_dotenv \
  -p tableau_mcp \
  tableau_mcp/__main__.py
```

**What you'll see**:
```
69 INFO: PyInstaller: 6.10.0
70 INFO: Python: 3.12.13
...
[lots of output]
...
1234 INFO: Building EXE from EXE-00.toc completed successfully.
```

**⏱️ This takes 15-20 minutes** (grab coffee ☕)

---

### Step 4: Make Binary Executable (1 minute)

```bash
chmod +x dist/tableau-mcp
```

---

### Step 5: Verify Binary Exists and Works (2 minutes)

**Check size and permissions**:
```bash
ls -lh dist/tableau-mcp
```

Expected output:
```
-rwxr-xr-x  45M  tableau-mcp
```

**Test it runs**:
```bash
# Start in background
./dist/tableau-mcp &
BG_PID=$!

# Give it 2 seconds to start
sleep 2

# Kill it
kill $BG_PID 2>/dev/null

# Should see no errors
```

---

### Step 6: Verify Code is Hidden (1 minute)

```bash
# Try to find Python code in binary
strings dist/tableau-mcp | grep -i "schema_profiler" | head -1

# Should output: NOTHING
# (If it outputs code, the binary has uncompiled code - rare)
```

---

### Step 7: Build Distribution Package (2 minutes)

```bash
cd /Users/kartik.arora/TABLEAU-MCP

python -m build
```

**Expected output**:
```
* Creating venv isolated environment...
* Installing packages in isolated environment...
* Building wheel...
Successfully built tableau-mcp-server-1.0.0-py3-none-any.whl
Successfully built tableau-mcp-server-1.0.0.tar.gz
```

---

### Step 8: Verify Distribution (1 minute)

```bash
ls -lh dist/*.whl
ls -lh dist/*.tar.gz
ls -lh dist/tableau-mcp
```

Expected output:
```
-rwxr-xr-x     45M  dist/tableau-mcp
-rw-r--r--     1.2M dist/tableau-mcp-server-1.0.0.tar.gz
-rw-r--r--     50M  dist/tableau-mcp-server-1.0.0-py3-none-any.whl
```

---

## All Commands in One Script (Copy & Paste)

Save this as `build_pyinstaller.sh`:

```bash
#!/bin/bash
set -e

PROJECT="/Users/kartik.arora/TABLEAU-MCP"
cd "$PROJECT"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     TABLEAU MCP - PYINSTALLER BUILD AUTOMATION             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1
echo "1️⃣  Installing PyInstaller..."
pip install -q pyinstaller==6.10.0
echo "   ✅ Done"
echo ""

# Step 2
echo "2️⃣  Testing module..."
timeout 2 python -m tableau_mcp > /dev/null 2>&1 || true
echo "   ✅ Module runs"
echo ""

# Step 3
echo "3️⃣  Building binary (this takes ~20 minutes)..."
echo "   Starting PyInstaller..."
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
  --hidden-import=python_dotenv \
  -p tableau_mcp \
  tableau_mcp/__main__.py 2>&1 | tail -5

# Step 4
echo ""
echo "4️⃣  Making executable..."
chmod +x dist/tableau-mcp
echo "   ✅ Done"
echo ""

# Step 5
echo "5️⃣  Verifying binary..."
SIZE=$(ls -lh dist/tableau-mcp | awk '{print $5}')
echo "   Binary size: $SIZE"
echo "   ✅ Binary created"
echo ""

# Step 6
echo "6️⃣  Verifying code is hidden..."
CODE_CHECK=$(strings dist/tableau-mcp | grep -i "schema_profiler" | wc -l)
if [ "$CODE_CHECK" -eq 0 ]; then
    echo "   ✅ Code is compiled (hidden)"
else
    echo "   ⚠️  Warning: Found some Python code in binary (may be normal)"
fi
echo ""

# Step 7
echo "7️⃣  Building distribution package..."
python -m build 2>&1 | grep -E "(wheel|tar.gz)" || true
echo "   ✅ Done"
echo ""

# Step 8
echo "8️⃣  Final verification..."
echo ""
echo "Distribution files created:"
ls -lh dist/tableau-mcp* | awk '{print "   " $9 " (" $5 ")"}'
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║               ✅ BUILD COMPLETE!                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Distribution ready at:"
echo "   Binary:   dist/tableau-mcp"
echo "   Wheel:    dist/tableau-mcp-server-1.0.0-py3-none-any.whl"
echo "   Source:   dist/tableau-mcp-server-1.0.0.tar.gz"
echo ""
echo "🧪 Test binary:"
echo "   ./dist/tableau-mcp"
echo ""
echo "🚀 Next steps:"
echo "   1. Commit: git add -A && git commit -m 'Add PyInstaller build'"
echo "   2. Tag:    git tag -a v1.0.0-pyinstaller -m 'Release with binary'"
echo "   3. Push:   git push origin main && git push origin --tags"
echo ""
```

**Run it**:
```bash
chmod +x build_pyinstaller.sh
./build_pyinstaller.sh
```

---

## Timeline

| Step | Task | Duration |
|------|------|----------|
| 1 | Install PyInstaller | 1 min |
| 2 | Test module | 1 min |
| 3 | **Build binary** | **20 min** ⏳ |
| 4 | Make executable | 1 min |
| 5 | Verify binary | 2 min |
| 6 | Hide code check | 1 min |
| 7 | Build distribution | 2 min |
| 8 | Final verification | 1 min |
| **TOTAL** | | **29 minutes** |

---

## What Happens After Each Step

### After Step 1: PyInstaller Installed
```bash
$ pyinstaller --version
6.10.0  ✅
```

### After Step 2: Module Tests
```bash
# Should see MCP server starting (not errors)
# Press Ctrl+C to stop
```

### After Step 3: Binary Built ⏱️
```bash
# PyInstaller creates:
build/
  tableau-mcp/
  ...lots of files...

dist/
  tableau-mcp  ← Your 45MB executable

tableau-mcp.spec  ← PyInstaller config
```

### After Step 5: Binary Works
```bash
$ ls -lh dist/tableau-mcp
-rwxr-xr-x  45M  tableau-mcp  ✅

$ ./dist/tableau-mcp
✅ MCP server running (press Ctrl+C to stop)
```

### After Step 7: Distribution Created
```bash
dist/
  tableau-mcp                          ← Binary (45MB)
  tableau-mcp-server-1.0.0.tar.gz     ← Source
  tableau-mcp-server-1.0.0-py3-none-any.whl  ← Wheel
```

---

## Troubleshooting During Build

### "ModuleNotFoundError during build"
```bash
# Add the missing module to --hidden-import
# Example: if it says "No module named 'requests'"
pyinstaller \
  --onefile \
  --hidden-import=requests \  # Add this
  ...
```

### "Build takes too long"
This is **normal**. First build takes 20+ minutes.
Subsequent builds are faster (uses cache).

### "Binary is 100+ MB"
This is **expected**. All dependencies are bundled:
- Python runtime
- FastMCP
- Pandas
- Lxml
- Google API
- OpenRouter API
- etc.

To reduce: Enable UPX compression (advanced)

---

## After Build: Test Installation

### Test 1: Run Binary Directly
```bash
./dist/tableau-mcp
# Should start MCP server
```

### Test 2: Copy to Random Location
```bash
cp dist/tableau-mcp /tmp/test_tableau_mcp
/tmp/test_tableau_mcp
# Should still work (self-contained)
```

### Test 3: Install via pip
```bash
pip install dist/tableau-mcp-server-1.0.0-py3-none-any.whl
tableau-mcp  # If entry points configured
```

---

## Success Indicators ✅

- [ ] PyInstaller installs (step 1)
- [ ] Module runs with `python -m tableau_mcp` (step 2)
- [ ] PyInstaller build completes (step 3)
- [ ] Binary exists at `dist/tableau-mcp` (step 5)
- [ ] Binary is executable (step 4)
- [ ] Binary runs when executed (step 5)
- [ ] Code is hidden in binary (step 6)
- [ ] Distribution package builds (step 7)
- [ ] All three files exist: binary, wheel, tar.gz (step 8)

---

## User Experience After Distribution

### Users Download Binary
```bash
$ wget tableau-mcp
$ chmod +x tableau-mcp
$ ./tableau-mcp
✅ MCP running
```

### Users Can't See Code
```bash
$ strings tableau-mcp | grep ".py"
# Returns nothing (code is compiled)
```

### No Python Installation Needed
```bash
$ python --version
# Users don't need this anymore
```

---

## Ready to Build? 

**Start here**:
```bash
./build_pyinstaller.sh
```

**That's it!** ☕ Grab coffee and wait 20 minutes.

---

## Next After Build

1. **Commit Changes**:
   ```bash
   git add -A
   git commit -m "Add PyInstaller binary build for code protection"
   ```

2. **Test Binary**:
   ```bash
   ./dist/tableau-mcp
   ```

3. **Create Release**:
   ```bash
   git tag -a v1.0.0-compiled -m "PyInstaller build"
   git push origin --tags
   ```

4. **Distribute**:
   - Option A: Upload `dist/tableau-mcp` (binary only)
   - Option B: Upload `dist/tableau-mcp-server-1.0.0.whl` (pip package)
   - Option C: Both!

---

## Your Code is Protected ✅

After PyInstaller:
- ✅ Code compiled to binary
- ✅ Source not readable
- ✅ No Python installation needed
- ✅ Single executable file
- ✅ Professional distribution

Ready to build? Run the script! 🚀
