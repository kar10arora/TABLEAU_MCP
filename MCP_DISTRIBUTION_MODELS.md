# MCP Distribution Models - CLI vs Module

## Your Question
> "How do Atlassian, Jira, Playwright MCPs work? Can I avoid exposing my code?"

## The Answer
There are **2 ways** MCPs are distributed. Your current approach is #1. You're asking about #2.

---

## Model 1: Module-Based (What You Have Now)

### How It Works
```bash
pip install tableau-mcp-server
```

Then Claude Code config:
```json
{
  "mcpServers": {
    "tableau": {
      "command": "python",
      "args": ["-m", "tableau_mcp.server"]
    }
  }
}
```

### What User Gets
- ✅ Full Python source code in site-packages
- ✅ Can read, learn from, modify your code
- ✅ Transparent, open-source style

### Code Exposure
- ❌ User can see all your source code
- ❌ User can see your algorithms
- ❌ User can see your implementation details

### Pros
- ✅ Open source friendly
- ✅ Community can contribute
- ✅ Easy to debug and inspect
- ✅ Good for collaborative projects

### Cons
- ❌ Code is visible to users
- ❌ Intellectual property exposed
- ❌ Implementation details are public

---

## Model 2: CLI-Based (Compiled/Executable)

### How It Works (Like Atlassian, Jira, Playwright)
```bash
pip install tableau-mcp-server
```

Then Claude Code config:
```json
{
  "mcpServers": {
    "tableau": {
      "command": "tableau-mcp"
    }
  }
}
```

### What Happens
```
user runs: tableau-mcp
    ↓
system calls: ~/.venv/bin/tableau-mcp
    ↓
runs: compiled executable or hidden Python code
    ↓
MCP server starts
```

### Code Exposure
- ✅ Source code is hidden/compiled
- ✅ User can't see your algorithms
- ✅ User can't see implementation details
- ✅ Intellectual property is protected

### Pros
- ✅ Code is hidden from users
- ✅ Intellectual property protected
- ✅ Looks like native command-line tool
- ✅ Professional distribution

### Cons
- ❌ Harder for users to debug
- ❌ Less transparent
- ❌ Community can't easily contribute

---

## Real-World Examples

### Atlassian MCP
```bash
pip install mcp-atlassian

# User runs:
# They just call the MCP server command
# Code is in a compiled executable or hidden
```

**Result**: Users don't see Atlassian's Python source code

### Playwright MCP
```bash
pip install playwright-mcp

# User runs the executable
# Users don't see how Playwright works internally
```

**Result**: Implementation is hidden

---

## How to Achieve Model 2 (Hidden Code)

### Step 1: Create Entry Point in setup.py

```python
setup(
    name="tableau-mcp-server",
    ...
    entry_points={
        'console_scripts': [
            'tableau-mcp=tableau_mcp.server:main',
        ],
    },
)
```

**What this does**: Creates command `tableau-mcp` that calls `tableau_mcp.server.main()`

### Step 2: Convert server.py to Have main() Function

**Current** (doesn't work with entry points):
```python
if __name__ == "__main__":
    mcp.run()
```

**New** (works with entry points):
```python
def main():
    mcp.run()

if __name__ == "__main__":
    main()
```

### Step 3: Claude Code Config

Users use:
```json
{
  "mcpServers": {
    "tableau": {
      "command": "tableau-mcp"
    }
  }
}
```

**Instead of**:
```json
{
  "mcpServers": {
    "tableau": {
      "command": "python",
      "args": ["-m", "tableau_mcp.server"]
    }
  }
}
```

---

## Step 3.5: Protecting Code (Optional)

If you want **real** code protection, you can:

### Option A: PyInstaller (Create Executable)
```bash
pip install pyinstaller
pyinstaller --onefile src/tableau_mcp/server.py
```
- Creates: `dist/tableau-mcp` (compiled executable)
- Users can't see Python code
- Code is truly hidden

### Option B: Cython (Compile to C)
```bash
pip install cython
# Compile Python to C
# Package as .so files
```
- Users get compiled binaries
- Original Python code not visible

### Option C: Standard Installation
```bash
# Just use entry_points
# Code is in site-packages (visible but organized)
```
- Code is visible but users don't typically read it
- Standard Python distribution

---

## Side-by-Side Comparison

| Feature | Model 1 (Module) | Model 2 (CLI) | Model 2+PyInstaller |
|---------|-----------------|---------------|-------------------|
| **Installation** | `pip install pkg` | `pip install pkg` | `pip install pkg` |
| **User Config** | `python -m mcp.server` | `tableau-mcp` | `tableau-mcp` |
| **Code Visible** | ✅ Yes (site-packages) | ✅ Yes (site-packages) | ❌ No (compiled) |
| **Complexity** | Low | Medium | High |
| **Effort to Setup** | 5 minutes | 15 minutes | 30+ minutes |
| **Professional** | ✅ Yes | ✅✅ Very | ✅✅✅ Most |
| **User-Friendly** | ✅ Yes | ✅✅ Better | ✅✅✅ Best |

---

## For Tableau MCP: My Recommendation

### If You're Starting Out
**Use Model 1** (Module-based):
```json
{
  "command": "python",
  "args": ["-m", "tableau_mcp.server"]
}
```
- ✅ Simple to implement
- ✅ Quick to distribute
- ✅ Works immediately
- ⏱️ Time: 5 minutes more

### If You Want Professional Distribution
**Use Model 2** (CLI-based):
```json
{
  "command": "tableau-mcp"
}
```
- ✅ Looks like native command
- ✅ More professional
- ✅ Users appreciate it
- ⏱️ Time: 15 minutes more

### If You Need Full Code Protection
**Use Model 2 + PyInstaller** (Compiled):
- ✅ Code is completely hidden
- ✅ Most professional
- ✅ Enterprise-ready
- ⏱️ Time: 45 minutes more

---

## Implementation for Model 2 (Recommended Middle Ground)

### Change 1: Update setup.py

```python
setup(
    name="tableau-mcp-server",
    version="1.0.0",
    ...
    entry_points={
        'console_scripts': [
            'tableau-mcp=tableau_mcp.server:main',
        ],
    },
)
```

### Change 2: Update server.py

```python
def main():
    """Entry point for CLI."""
    mcp.run()

if __name__ == "__main__":
    main()
```

### Change 3: User's Claude Code Config

```json
{
  "mcpServers": {
    "tableau": {
      "command": "tableau-mcp",
      "env": {
        "GEMINI_API_KEY": "sk-..."
      }
    }
  }
}
```

### Result After pip install
```bash
# User gets a command:
$ which tableau-mcp
/Users/username/.venv/bin/tableau-mcp

$ tableau-mcp
INFO: Started server process...
```

**Advantage**: Looks like a native tool, not `python -m something`

---

## How Official MCPs Do It

### Atlassian MCP Structure
```
setup.py:
    entry_points = {
        'console_scripts': ['atlassian-mcp=atlassian_mcp:main']
    }

User runs:
    atlassian-mcp

Claude Code sees:
    $ which atlassian-mcp
    /venv/bin/atlassian-mcp
    
    $ atlassian-mcp
    MCP server running...
```

### Playwright MCP Structure
```
setup.py:
    entry_points = {
        'console_scripts': ['playwright-mcp=playwright_mcp.server:main']
    }

User runs:
    playwright-mcp

Claude Code sees:
    $ which playwright-mcp
    /venv/bin/playwright-mcp
```

---

## Your Current Code Visibility

### Model 1 (Current)
```bash
pip install tableau-mcp-server
ls ~/.venv/lib/python3.x/site-packages/tableau_mcp/
# User sees:
# __init__.py
# server.py      ← Can read this
# paths.py       ← Can read this
# core/          ← Can read all this
# llm/           ← Can read all this
# templates/     ← Can read template logic
```

### Model 2 (CLI)
```bash
pip install tableau-mcp-server
ls ~/.venv/lib/python3.x/site-packages/tableau_mcp/
# Same files visible, BUT:
# Users call: tableau-mcp
# Not: python -m tableau_mcp.server
# Looks more professional
```

### Model 3 (Compiled with PyInstaller)
```bash
pip install tableau-mcp-server
ls ~/.venv/bin/
# User sees:
# tableau-mcp  ← Binary executable, NOT readable Python
# Users can't see source code at all
```

---

## My Recommendation for You

### Right Now (Phase 1)
Use **Model 1 (Module-based)**:
```json
{
  "command": "python",
  "args": ["-m", "tableau_mcp.server"],
  "env": {"GEMINI_API_KEY": "sk-..."}
}
```

**Why**: 
- ✅ Simple, works now
- ✅ Good for learning/feedback
- ✅ Easier for users to debug issues

### Later (Phase 2)
Upgrade to **Model 2 (CLI-based)**:
```json
{
  "command": "tableau-mcp",
  "env": {"GEMINI_API_KEY": "sk-..."}
}
```

**Changes needed**: 
- Add `entry_points` to setup.py
- Add `def main()` to server.py
- 15 minutes of work

### Phase 3 (Enterprise)
If needed: Compile with **PyInstaller**
- 45 minutes of work
- Complete code protection

---

## Decision Matrix

```
Do you want users to:          Use Model:
├─ Learn from your code?       → Model 1 (Module)
├─ Use without complexity?     → Model 2 (CLI)
├─ See zero code?              → Model 3 (Compiled)
└─ Professional looking?       → Model 2 (CLI)
```

---

## What's Best for Tableau MCP?

Given that:
- ✅ It's a data transformation tool
- ✅ Users want professional MCPs
- ✅ Code isn't super sensitive
- ✅ You want adoption

**Recommendation: Model 2 (CLI)**

```json
{
  "command": "tableau-mcp",
  "env": {"GEMINI_API_KEY": "sk-..."}
}
```

This is what:
- ✅ Looks professional
- ✅ Matches other MCPs
- ✅ Still allows users to help debug
- ✅ Takes 15 minutes to implement

---

## Bottom Line

| Question | Answer |
|----------|--------|
| **Is my code exposed?** | Yes, in Model 1 & 2. No, in Model 3. |
| **Should I use Model 3?** | Only if truly necessary (enterprise). |
| **Which do official MCPs use?** | Most use Model 2 (CLI). |
| **Which should you use?** | Model 2 (CLI) - professional middle ground. |
| **How long to upgrade from Model 1→2?** | 15 minutes. |

---

## Next Steps

### Option A: Stay with Model 1 (Now)
```json
{"command": "python", "args": ["-m", "tableau_mcp.server"]}
```
- Test and refine
- Users can give feedback on code

### Option B: Upgrade to Model 2 (Add 15 minutes)
```json
{"command": "tableau-mcp"}
```
- Looks professional
- Matches official MCPs
- Still transparent

### Option C: Full Protection with Model 3 (Add 45 minutes)
```json
{"command": "tableau-mcp"}
```
- But compiled as binary
- Code completely hidden
- Enterprise-ready

**What do you want to do?**
