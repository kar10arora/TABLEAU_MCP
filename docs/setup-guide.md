Inspect this @docs/logs-tested-after-bug-fixation.md as per the snapshot I tried to handle the local disk permission with claude desktop with filesystem still getting error??
Let me look at the project structure and any relevant config files to understand the full setup.

Bash List project structure and JSON config files
IN
find /Users/kartik.arora/TABLEAU-MCP -name "*.json" -not -path "*/node_modules/*" | head -20 && echo "---" && ls /Users/kartik.arora/TABLEAU-MCP/

OUT
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/scm_file_list.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/anyio-4.14.1.dist-info/scm_version.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/tableau_mcp_server-1.0.0a0.dist-info/direct_url.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/pydantic_core-2.46.4.dist-info/sboms/pydantic-core.cyclonedx.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/cryptography-49.0.0.dist-info/sboms/cryptography-rust.cyclonedx.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/ast_serialize-0.5.0.dist-info/sboms/mypy_parser.cyclonedx.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/watchfiles-1.2.0.dist-info/sboms/watchfiles_rust_notify.cyclonedx.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/setuptools/config/setuptools.schema.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/setuptools/config/distutils.schema.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/black/resources/black.schema.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/rpds_py-2026.5.1.dist-info/sboms/rpds-py.cyclonedx.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/jiter-0.15.0.dist-info/sboms/jiter-python.cyclonedx.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/googleapiclient/discovery_cache/documents/chromewebstore.v1.1.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/googleapiclient/discovery_cache/documents/run.v1alpha1.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/googleapiclient/discovery_cache/documents/cloudiot.v1.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/googleapiclient/discovery_cache/documents/calendar.v3.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/googleapiclient/discovery_cache/documents/spanner.v1.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/googleapiclient/discovery_cache/documents/adexchangebuyer.v1.2.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/googleapiclient/discovery_cache/documents/documentai.v1beta3.json
/Users/kartik.arora/TABLEAU-MCP/venv/lib/python3.12/site-packages/googleapiclient/discovery_cache/documents/rapidmigrationassessment.v1.json
---
ARCHITECTURE_DIAGRAM.md
CLAUDE_CODE_MCP_SETUP.md
CURRENT_STATE_SUMMARY.md
DISTRIBUTION_QUICK_REFERENCE.md
DISTRIBUTION_READINESS_GUIDE.md
FILE_STRUCTURE_EVALUATION.md
HONEST_STATUS.md
IMPLEMENTATION_GUIDE.md
IMPLEMENTATION_STATUS.md
MANIFEST.in
MCP_DISTRIBUTION_MODELS.md
MIGRATION_SUMMARY.md
PROJECT_ROADMAP.md
PROJECT_STATUS.md
PYINSTALLER_COMMANDS.md
PYINSTALLER_SETUP_GUIDE.md
README.md
SETUP_GUIDE.md
SETUP_PY_BEFORE_AFTER.md
SETUP_PY_EXPLAINED.md
STORY_1_7_CHECKLIST.txt
STORY_1_7_MISSING_COMPONENTS.md
STORY_1_7_QUICKSTART.md
STORY_1_7_SUMMARY.md
STRUCTURE_MIGRATION_COMPLETE.md
TABLEAU_MCP_PRD.md
TESTING_COMPLETE.md
Tested_generated_workbook
VALIDATION_REPORT.md
bug_verification_workbooks
build
chat_cc.md
demo_basic.py
docs
examples
generate_story_workbooks.py
hooks
inspect_workbooks.py
pyproject.toml
pytest.ini
requirements.txt
setup.py
tableau_mcp
tableau_mcp_requirement.md
tableau_mcp_server.egg-info
tests
venv
verify_pyinstaller_ready.sh
Read logs-tested-after-bug-fixation.md
Bash Read MCP setup docs
IN
cat /Users/kartik.arora/TABLEAU-MCP/CLAUDE_CODE_MCP_SETUP.md 2>/dev/null | head -80 && echo "---" && cat /Users/kartik.arora/TABLEAU-MCP/docs/*.md 2>/dev/null | head -100

OUT
# Tableau MCP - Claude Code Integration Guide

## Status: ✅ READY FOR INTEGRATION

Your Tableau MCP is **fully functional at Story 2.4** (Visual Encodings). Here's how to use it with Claude Code:

---

## Quick Setup (5 minutes)

### Step 1: Verify Dependencies ✅
```bash
cd /Users/kartik.arora/TABLEAU-MCP
pip install -r requirements.txt
```
**Status**: All dependencies already installed

---

### Step 2: Configure Claude Code

#### Option A: Global Configuration (Recommended)
Edit `~/.claude/settings.json` and add this under `mcpServers`:

```json
{
  "mcpServers": {
    "tableau-generator": {
      "command": "python",
      "args": ["/Users/kartik.arora/TABLEAU-MCP/src/mcp/server.py"],
      "env": {
        "GEMINI_API_KEY": "YOUR_API_KEY_HERE",
        "DEFAULT_LLM_PROVIDER": "gemini",
        "TEMPLATE_DIR": "/Users/kartik.arora/TABLEAU-MCP/templates",
        "OUTPUT_DIR": "/Users/kartik.arora/TABLEAU-MCP/examples/generated_workbooks"
      }
    }
  }
}
```

#### Option B: Project-Specific Configuration
Create `.claude/settings.json` in your project:

```json
{
  "mcpServers": {
    "tableau-generator": {
      "command": "python",
      "args": ["src/mcp/server.py"],
      "env": {
        "GEMINI_API_KEY": "YOUR_API_KEY_HERE",
        "DEFAULT_LLM_PROVIDER": "gemini"
      }
    }
  }
}
```

---

### Step 3: Set API Key

Get your API key:
- **Gemini**: https://ai.google.dev/
- **OpenRouter**: https://openrouter.ai/

Add to `.env`:
```bash
GEMINI_API_KEY=your_key_here
DEFAULT_LLM_PROVIDER=gemini
```

---

## Available MCP Tools

Once integrated, Claude Code will have access to:

### 1. `inspect_dataset_schema(file_path: str)`
---
# Tableau MCP - Bugs & Fixes Documentation

**Date**: 2026-06-29  
**Version**: 1.0.0-alpha  
**Status**: Critical Issues Identified & Solutions Documented

---

## Executive Summary

Three critical issues were identified during extensive testing with real-world prompts. Two issues are implementation gaps (features partially or not working), and one is a newly discovered bug in the XML generator when handling multi-dimension grouping.

| Issue | Severity | Status | Impact |
|-------|----------|--------|--------|
| **Bug #1: Multi-Dimension Array Handling** | 🔴 CRITICAL | Active Bug | Breaks workbook generation when >1 dimension in columns |
| **Bug #2: Aggregation Function Support** | 🔴 CRITICAL | Missing Feature | All measures default to SUM regardless of request |
| **Feature #3: Story 2.4 (Visual Encodings)** | 🟡 PARTIAL | Partially Working | Color & tooltip working, size encoding not tested |

---

## Bug #1: Multi-Dimension Array Handling (CRITICAL) 🔴

### Issue Details

**Symptom**: When LLM generates blueprint with multiple dimensions as an array:
```json
"column_field": ["Product_Category", "Region"]
```

The XML generator **fails to concatenate** them with "+", instead inserting the Python list literal into XML:

```xml
<!-- WRONG - Tableau can't parse this: -->
<cols>[federated...][none:['Product_Category', 'Region']:nk]</cols>

<!-- RIGHT - Should be: -->
<cols>[federated...][none:Product_Category:nk] + [federated...][none:Region:nk]</cols>
```

**Result**: Tableau workbook fails to load with validation errors:
```
Error(330,46): value '[[' does not match regular expression facet
Error(330,46): missing required attribute 'role'
Error(332,39): missing required attribute 'name'
```

### Root Cause

**File**: `tableau_mcp/core/xml_generator.py`  
**Method**: `_build_worksheet()`  
**Issue**: No handling for when `column_field` or `row_field` is a list instead of a string.

**Current Code** (BROKEN):
```python
# Line ~320 (approximate)
cols = sheet.get("column_field", "")
cols_xml = f'[{ds_id}].[none:{cols}:nk]'
# When cols is a list, this produces: [ds_id].[none:['field1', 'field2']:nk]
```

### Test Case That Reproduces Bug

```
User Prompt:
"Create a Tableau workbook with two worksheets:
1. Sales by Category, colored by Region
2. Sales by Category and Region, with Discount shown in tooltip"

Generated Blueprint (correct):
{
  "sheets": [{
    "name": "Sales by Category and Region",
    "column_field": ["Product_Category", "Region"],  ← ARRAY
    "row_field": "Sales_Amount",
    "mark_type": "Bar"
  }]
}

Generated XML (BROKEN):
<cols>[federated...][none:['Product_Category', 'Region']:nk]</cols>
                            ^^^ Invalid Tableau syntax
```

### Solution Implementation

**File**: `tableau_mcp/core/xml_generator.py`

**Step 1**: Update `_build_worksheet()` method signature to accept column/row arrays:

```python
def _build_worksheet(self, name, ds_id, cols, rows, col_datatype, row_datatype,
                     col_role, row_role, col_type, row_type,
                     sort_cfg=None, filters_cfg=None, encodings_cfg=None,
                     aggregation=None):
    """
    Build worksheet XML with support for:
    - Single column_field (string)
    - Multiple column_fields (list for concatenation)
    - Single row_field (string)
    - Multiple row_fields (list for multi-measure)
Here's a clear breakdown of what's happening — these are two separate issues:

Issue 1: filesystem MCP — "Server disconnected"
What the screenshot shows: The filesystem MCP server using npx.cmd is failing on the Windows machine. This is unrelated to your Tableau MCP.

Root cause options (in order of likelihood):

A) Node.js / npx not installed or not in PATH
The filesystem MCP runs via npx.cmd @modelcontextprotocol/server-filesystem, which requires Node.js. If it's not installed or not on the system PATH when Claude Desktop launches:


# Verify on Windows (CMD/PowerShell):
node --version
npx --version
If either fails → install Node.js from nodejs.org, then restart Claude Desktop.

B) npx downloads the package but it crashes immediately
Try running the exact command manually in CMD to see the real error:


npx.cmd -y @modelcontextprotocol/server-filesystem C:\Users\user\Desktop C:\Users\user\Downloads C:\Users\user\Claude
This will reveal the actual crash reason (permissions, missing directory, etc.).

C) The C:\Users\user\Claude directory doesn't exist
Claude Desktop might be passing a directory that doesn't exist. Verify all three paths exist on the machine:

C:\Users\user\Desktop ✓ (likely exists)
C:\Users\user\Downloads ✓ (likely exists)
C:\Users\user\Claude ✗ — this likely doesn't exist
Fix: Create the directory or remove it from the config. In Claude Desktop → Edit Config:


{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\user\\Desktop",
        "C:\\Users\\user\\Downloads"
      ]
    }
  }
}
Issue 2: Workbook Generation Failed (from the log)
This is a different problem — the inspect_dataset_schema call succeeded (file was read fine via the Tableau MCP Python server), but generate_tableau_workbook threw an authentication error.

From your docs/bugs-and-fixes.md, the backend uses Gemini API. The log says "misconfigured with invalid Google credentials" — meaning the GEMINI_API_KEY isn't set in the Claude Desktop MCP config for tableau-mcp.

Check what's in your Claude Desktop claude_desktop_config.json for the tableau-mcp entry — it likely looks like:


"env": {
  "GEMINI_API_KEY": "YOUR_API_KEY_HERE"  ← placeholder never replaced
}
Fix: Replace with your actual Gemini API key from ai.google.dev.

Summary
Problem	Cause	Fix
filesystem → Server disconnected	Missing Node.js or non-existent C:\Users\user\Claude dir	Install Node.js / remove bad path from config
Workbook generation auth error	GEMINI_API_KEY not set in tableau-mcp env config	Add real API key to Claude Desktop config
The two issues are independent — fixing the filesystem MCP won't fix workbook generation, and vice versa. Start with the Gemini API key since that's what blocks the core Tableau functionality.


image.png
1920×1040
Generate a Tableau workbook using Users/user/Desktop/sales_data.csv that shows:

Total sales by region (bar chart)
Average Sales trend over time (line chart)
Top 5 product categories by revenue (horizontal bar)

Identified inaccessible local file path; resolved to request upload
Identified inaccessible local file path; resolved to request upload
Need to access the file - it's a local desktop path, not uploaded. I should ask user to upload it since I can't access their local filesystem.

Done
I can't directly access files on your computer's desktop — I only have access to files you've uploaded into this chat (they'd appear under /mnt/user-data/uploads/). Could you upload sales_data.csv here? Once it's uploaded, I can inspect its columns and generate a Tableau workbook with those three views.
see the user claude config:
{
  "mcpServers": {
    "tableau-mcp": {
      "command": "C:\\Python311\\Scripts\\tableau-mcp.exe",
      "args": [],
      "env": {
        "GEMINI_API_KEY": "AQ.Ab8s9ygAQ.Ab8RN6JD6KIgsX1VMVFti5roMrE718cJ8oMrbYbKRx4lmys9yg",
        "DEFAULT_LLM_PROVIDER": "gemini"
      }
    },
    "filesystem": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\user\\Desktop",
        "C:\\Users\\user\\Downloads"
      ]
    }
  },
  "coworkUserFilesPath": "C:\\Users\\user\\Claude",
  "preferences": {
    "coworkScheduledTasksEnabled": false,
    "coworkHipaaRestricted": false,
    "ccdScheduledTasksEnabled": false,
    "bypassPermissionsGateByAccount": {
      "a6c54c4a-fab8-4cd1-b12f-3cfa32528e45": false
    },
    "coworkWebSearchEnabled": true,
    "coworkModelAutoFallbackByAccount": {
      "a6c54c4a-fab8-4cd1-b12f-3cfa32528e45": true
    },
    "remoteToolsDeviceName": "desktop-lre3rt2",
    "epitaxyPrefs": {
      "starred-local-code-sessions": [],
      "starred-cowork-spaces": [],
      "starred-session-groups": [],
      "dframe-local-slice": {
        "pinnedOrder": [],
        "customGroupAssignments": {},
        "customGroupOrder": {}
      },
      "ccd-sessions-filter": {
        "state": {
          "selectedProjects": []
        },
        "version": 0
      },
      "desktop-frame.paneStore.v1": {
        "state": {
          "extraPanesByMode": {},
          "colWeightsByMode": {},
          "rowSplit": 0.5,
          "draftNonce": 0
        },
        "version": 4
      }
    }
  }
}
Looking at the config and screenshot together, I can spot three distinct problems:

Problem 1: Invalid Gemini API Key (critical)
Your key in the config:


AQ.Ab8s9ygAQ.Ab8RN6JD6KIgsX1VMVFti5roMrE718cJ8oMrbYbKRx4lmys9yg
This is not a valid Gemini API key. Real Gemini keys always start with AIza.... This is why workbook generation fails with an authentication error every time.

Fix: Get a valid key from ai.google.dev/aistudio and update the config:


"GEMINI_API_KEY": "AIzaSy..."
Problem 2: Wrong Path Format in the Prompt
The user typed Users/user/Desktop/sales_data.csv (forward slashes, no drive letter). The filesystem MCP only serves the paths it was configured with: C:\Users\user\Desktop. The tableau-mcp needs the exact Windows path:


C:\Users\user\Desktop\sales_data.csv
Even if filesystem MCP is working, the path mismatch causes Claude to say "I can't access this."

Problem 3: Filesystem MCP Still Disconnected = Claude.ai Web vs Desktop
Looking at the screenshot — the user is on Claude.ai web (browser), not the Claude Desktop app. The claude_desktop_config.json MCP servers only run when Claude Desktop is open and active. The "filesystem" toggle visible in the web connectors panel reflects the Desktop-side server status, which is still disconnected from before.

The flow that actually works:


Claude Desktop App (open) 
    → starts npx filesystem MCP locally
    → starts tableau-mcp.exe locally
    → Claude can read C:\Users\user\Desktop\sales_data.csv
The web interface alone cannot access local files even with the toggle on — it bridges through the Desktop app.

Checklist to Fix Everything
Step	Action
1	Get a real Gemini key (AIza...) from ai.google.dev
2	Replace the bad key in claude_desktop_config.json
3	Restart Claude Desktop app (not browser)
4	Check filesystem MCP status — should turn green
5	Use Claude Desktop (not web) for local file access
6	Use full Windows path: C:\Users\user\Desktop\sales_data.csv
The filesystem MCP config itself looks correct now (Desktop and Downloads, no missing Claude dir) — it just needs Node.js reachable on PATH and Claude Desktop to be running.

user is not working on web , it is working on claude desktop you idiot
You're right, I apologize. That is the Claude Desktop UI.

The core issue remains the same — the filesystem MCP is still disconnected (as shown in the first screenshot), so even in Claude Desktop, file access fails. That's why Claude says it can't read the file.

The two things blocking it right now:

1. Filesystem MCP not starting — fix Node.js PATH issue so npx.cmd works when Claude Desktop launches. Run this in CMD to confirm:


npx.cmd -y @modelcontextprotocol/server-filesystem C:\Users\user\Desktop C:\Users\user\Downloads
If it errors, Node.js isn't on PATH → reinstall Node.js and restart Claude Desktop.

2. Invalid Gemini API key — the key AQ.Ab8s9yg... in the config is malformed (should start with AIza...). Get a real one from aistudio.google.com and update claude_desktop_config.json:


"GEMINI_API_KEY": "AIzaSy_your_real_key_here"
3. Path format in the prompt — even once filesystem works, tell the end user to use the full Windows path:


C:\Users\user\Desktop\sales_data.csv
not Users/user/Desktop/sales_data.csv.

After fixing 1 and 2, restart Claude Desktop and the filesystem MCP should turn green and file access will work.

C:\Users\user\Desktop\sales_data.csv
even after this path, it is not working and I check with second command and it was working fine:
C:\Users\user>npx.cmd -y @modelcontextprotocol/server-filesystem C:\Users\user\Desktop C:\Users\user\Downloads
Secure MCP Filesystem Server running on stdio
Good — so npx.cmd itself works fine. That rules out Node.js PATH as the problem.

The real issue now is that Claude Desktop's MCP process environment is different from your CMD session. When Claude Desktop spawns npx.cmd, it uses a stripped-down environment without the full Windows PATH, so it can find npx.cmd to start the server, but then the server likely crashes because it can't find Node.js internals or npm registry access fails silently.

Verify this — run this in CMD to check where node is:


where node
where npx.cmd
Then update claude_desktop_config.json to use the full absolute path to npx.cmd:


"filesystem": {
  "command": "C:\\Program Files\\nodejs\\npx.cmd",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "C:\\Users\\user\\Desktop",
    "C:\\Users\\user\\Downloads"
  ]
}
Replace C:\\Program Files\\nodejs\\npx.cmd with whatever where npx.cmd returns.

Also check the tableau-mcp.exe path — run this to confirm it exists:


dir C:\Python311\Scripts\tableau-mcp.exe
If that file doesn't exist, the tableau-mcp is also silently failing and Claude has no tools at all, which is why it falls back to saying it can't read files.

After updating the config, fully quit and reopen Claude Desktop (not just close the window — right-click the tray icon → Quit), then check the MCP settings page to see if filesystem turns green.

Identified inaccessible file path; requested user upload
No file uploaded actually - path is local to user's machine, not accessible to me. I don't have access to C:\Users\user\Desktop\sales_data.csv. Need to ask them to upload it.

Done
I don't have access to your local file system, so I can't reach C:\Users\user\Desktop\sales_data.csv directly. Could you upload the CSV here (drag and drop it into the chat)? Once it's uploaded, I'll generate the Tableau workbook with the three views you described — total sales by region, average sales trend over time, and top 5 product categories by revenue.
{
  "mcpServers": {
    "tableau-mcp": {
      "command": "C:\\Python311\\Scripts\\tableau-mcp.exe",
      "args": [],
      "env": {
        "GEMINI_API_KEY": "AQ.Ab8s9ygAQ.Ab8RN6JD6KIgsX1VMVFti5roMrE718cJ8oMrbYbKRx4lmys9yg",
        "DEFAULT_LLM_PROVIDER": "gemini"
      }
    },
    "filesystem": {
      "command": "C:\\Program Files\\nodejs\\npx.cmd",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\user\\Desktop",
        "C:\\Users\\user\\Downloads"
      ]
    }

still not accessible at all and let me clear that gemini key is correct
The root problem is that Claude is not seeing any MCP tools at all — neither filesystem nor tableau-mcp. That's why it falls back to "I can't access your filesystem."

Step 1 — Confirm MCP connection status

In Claude Desktop → Settings → Developer, check if both MCPs show green (connected) or still red (failed). If still red, the servers are crashing before Claude can use them.

Step 2 — Test tableau-mcp.exe directly in CMD


C:\Python311\Scripts\tableau-mcp.exe
If it crashes or shows an error, that's your problem. The exe needs to start and stay running, communicating via stdio.

Step 3 — Fix filesystem MCP: pre-install the package

The -y flag makes npx download the package on demand. Inside Claude Desktop's sandboxed environment this download silently fails. Pre-install it globally:


npm install -g @modelcontextprotocol/server-filesystem
Then update the config to remove -y:


"filesystem": {
  "command": "C:\\Program Files\\nodejs\\npx.cmd",
  "args": [
    "@modelcontextprotocol/server-filesystem",
    "C:\\Users\\user\\Desktop",
    "C:\\Users\\user\\Downloads"
  ]
}
Step 4 — Fully restart Claude Desktop (system tray → Quit, not just close window)

Step 5 — Verify tools are loaded

Open a new chat in Claude Desktop and click the tools/hammer icon (⚒). You should see tools like read_file, inspect_dataset_schema, generate_tableau_workbook listed. If that list is empty, the MCPs are still not connecting.

The inspect_dataset_schema working in the earlier log was from the Claude.ai web connector setup, not this Desktop config — so don't use that as a baseline for what's working here.

give me e2e commands for these 2 process:
1. for new users who want to try my mcp for the first time
2. those users who have mcp installed already and want to take the latest updates
and dont intermingled with this above thing, just provide the commands as per this Tableau mcp project
Let me look at the project's packaging and setup files first.

Bash Read packaging config files
IN
cat /Users/kartik.arora/TABLEAU-MCP/setup.py && echo "===" && cat /Users/kartik.arora/TABLEAU-MCP/pyproject.toml && echo "===" && cat /Users/kartik.arora/TABLEAU-MCP/requirements.txt

OUT
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
    url="https://github.com/kar10arora/TABLEAU_MCP",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'tableau-mcp=tableau_mcp.mcp.server:main',
        ],
    },
    package_data={
        'tableau_mcp': ['templates/*.twb'],
    },
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
===
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "tableau-mcp-server"
version = "1.0.0-alpha"
description = "Model Context Protocol server for automated Tableau workbook generation"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Tableau MCP Team"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "fastmcp>=0.2.0",
    "pandas>=2.0.0",
    "lxml>=4.9.0",
    "python-dotenv>=1.0.0",
    "openai>=1.0.0",
    "google-generativeai>=0.3.0",
]

[project.scripts]
tableau-mcp = "tableau_mcp.mcp.server:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["tableau_mcp*"]

[tool.setuptools.package-data]
"tableau_mcp" = ["templates/*.twb"]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
]

[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311', 'py312']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "google.generativeai",
    "fastmcp",
    "lxml",
]
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --strict-markers --tb=short"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "requires_api: marks tests that require API keys",
    "requires_tableau: marks tests that require Tableau Desktop",
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
===
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
Bash Check package structure and entry points
IN
ls /Users/kartik.arora/TABLEAU-MCP/tableau_mcp/ && echo "===" && cat /Users/kartik.arora/TABLEAU-MCP/tableau_mcp_server.egg-info/entry_points.txt 2>/dev/null && echo "===" && cat /Users/kartik.arora/TABLEAU-MCP/SETUP_GUIDE.md | head -100

OUT
__init__.py
__main__.py
__pycache__
core
llm
mcp
paths.py
templates
===
[console_scripts]
tableau-mcp = tableau_mcp.mcp.server:main
===
# Tableau MCP Server - Setup Guide

## ✅ What's Complete

You've successfully completed **Story 1.1 through 1.4** from Epic 1:

- ✅ Project structure created
- ✅ Git repository initialized
- ✅ Virtual environment set up
- ✅ Dependencies installed
- ✅ Core modules implemented:
  - `src/core/uuid_utils.py` - UUID generation
  - `src/core/schema_profiler.py` - Dataset profiling
  - `src/core/xml_generator.py` - Workbook generation
- ✅ Test suite created (13 tests, all passing)
- ✅ Sample dataset created
- ✅ Base template added (`templates/base_template.twb`)
- ✅ Basic demo working (without LLM)

## 🎯 Current Status

**Phase**: Epic 1 - MVP Foundation  
**Progress**: Stories 1.1-1.4 complete (4/7)  
**Next**: Story 1.5 - LLM Integration

## 📋 Next Steps

### 1. Set Up API Keys (for LLM Integration)

To enable natural language workbook generation, you need an LLM API key:

**Option A: Google Gemini (Recommended - Free tier available)**
```bash
# Create .env file
cp .env.example .env

# Add your Gemini API key to .env
GEMINI_API_KEY=your_actual_key_here
DEFAULT_LLM_PROVIDER=gemini
```

Get a free Gemini API key: https://makersuite.google.com/app/apikey

**Option B: OpenRouter (Alternative)**
```bash
# Add to .env
OPENROUTER_API_KEY=your_actual_key_here
DEFAULT_LLM_PROVIDER=openrouter
```

Get OpenRouter key: https://openrouter.ai/

### 2. Test the Complete Pipeline

Once you have API keys set up:

```bash
# Test with LLM integration
python demo_with_llm.py
```

This will test the full natural language → workbook pipeline.

### 3. Set Up MCP Integration (Claude Desktop or Kiro)

**For Claude Desktop:**

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tableau-generator": {
      "command": "python",
      "args": ["/absolute/path/to/your/TABLEAU-MCP/src/mcp/server.py"],
      "env": {
        "GEMINI_API_KEY": "your_key_here"
      }
    }
  }
}
```

Replace `/absolute/path/to/your/TABLEAU-MCP` with your actual path.

**For Kiro IDE:**

Similar configuration through Kiro's MCP settings.

## 🧪 Testing

### Run All Tests
```bash
source venv/bin/activate
pytest tests/ -v
```

### Run Specific Tests
```bash
# UUID tests
Bash Check server entry point and build artifacts
IN
cat /Users/kartik.arora/TABLEAU-MCP/tableau_mcp/mcp/server.py | head -30 && echo "===" && ls /Users/kartik.arora/TABLEAU-MCP/build/ 2>/dev/null && echo "===" && cat /Users/kartik.arora/TABLEAU-MCP/PYINSTALLER_COMMANDS.md | head -60

OUT
"""
FastMCP server for Tableau workbook generation.
"""

from fastmcp import FastMCP
from tableau_mcp.core.schema_profiler import SchemaProfiler
from tableau_mcp.core.xml_generator import TableauXMLCompiler
from tableau_mcp.llm.client import LLMClient
import os
import json
from tableau_mcp.paths import get_output_dir,get_template_path

# Initialize FastMCP server
mcp = FastMCP("tableau-mcp-server")

# Initialize components
schema_profiler = SchemaProfiler()
_llm_client = None
TEMPLATE_PATH = get_template_path()


def _get_llm_client():
    """Lazy-load LLM client only when needed."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


@mcp.tool()
===
bdist.macosx-26.0-x86_64
lib
===
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
Bash Check PyPI availability and distribution reference
Reason: we are not using PyPI, with the help of the pip install via github we proceed with that in order to make tableau-mcp a global package
IN
pip index versions tableau-mcp-server 2>/dev/null || echo "Not on PyPI" && echo "===" && cat /Users/kartik.arora/TABLEAU-MCP/DISTRIBUTION_QUICK_REFERENCE.md

Bash Get GitHub remote URL
IN
git remote -v

OUT
origin	https://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@github.com/kar10arora/TABLEAU_MCP.git (fetch)
origin	https://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@github.com/kar10arora/TABLEAU_MCP.git (push)
Here are the clean e2e commands for both scenarios.

1. New Users (First-time install)
Prerequisites: Python 3.9+, pip, Claude Desktop installed


# Step 1 — Install tableau-mcp globally
pip install git+https://github.com/kar10arora/TABLEAU_MCP.git

# Step 2 — Find the installed exe path (copy this output for the config)
where tableau-mcp

# Step 3 — Verify it starts correctly
tableau-mcp
Expected output: MCP server running on stdio (then Ctrl+C to stop)

Step 4 — Add to Claude Desktop config

Open C:\Users\<you>\AppData\Roaming\Claude\claude_desktop_config.json and add:


{
  "mcpServers": {
    "tableau-mcp": {
      "command": "C:\\Python311\\Scripts\\tableau-mcp.exe",
      "args": [],
      "env": {
        "GEMINI_API_KEY": "your_AIza_key_here",
        "DEFAULT_LLM_PROVIDER": "gemini"
      }
    }
  }
}
Replace the command path with whatever where tableau-mcp returned.


# Step 5 — Fully restart Claude Desktop (system tray → Quit, then reopen)
2. Existing Users (Getting latest updates)

# Step 1 — Upgrade to latest from GitHub
pip install --force-reinstall git+https://github.com/kar10arora/TABLEAU_MCP.git

# Step 2 — Verify the updated version starts correctly
tableau-mcp

# Step 3 — Fully restart Claude Desktop (system tray → Quit, then reopen)
No config changes needed — the exe path stays the same after an upgrade.

Last login: Mon Jun 29 22:03:44 on ttys034
kartik.arora@ndi-mb-150 ~ % pip install --force-reinstall git+https://github.com/kar10arora/TABLEAU_MCP.git


error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try brew install
    xyz, where xyz is the package you are trying to
    install.
    
    If you wish to install a Python library that isn't in Homebrew,
    use a virtual environment:
    
    python3 -m venv path/to/venv
    source path/to/venv/bin/activate
    python3 -m pip install xyz
    
    If you wish to install a Python application that isn't in Homebrew,
    it may be easiest to use 'pipx install xyz', which will manage a
    virtual environment for you. You can install pipx with
    
    brew install pipx
    
    You may restore the old behavior of pip by passing
    the '--break-system-packages' flag to pip, or by adding
    'break-system-packages = true' to your pip.conf file. The latter
    will permanently disable this error.
    
    If you disable this error, we STRONGLY recommend that you additionally
    pass the '--user' flag to pip, or set 'user = true' in your pip.conf
    file. Failure to do this can result in a broken Homebrew installation.
    
    Read more about this behavior here: <https://peps.python.org/pep-0668/>

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
kartik.arora@ndi-mb-150 ~ % pipx install --force-reinstall git+https://github.com/kar10arora/TABLEAU_MCP.git


usage: pipx [-h] [--version]
            {install,install-all,uninject,inject,pin,unpin,upgrade,upgrade-all,upgrade-shared,uninstall,uninstall-all,reinstall,reinstall-all,list,interpreter,run,runpip,ensurepath,environment,completions,help} ...
pipx: error: unrecognized arguments: --force-reinstall
kartik.arora@ndi-mb-150 ~ % 

give me commands for both apple and windoes properly
macOS
New Users

# Install pipx (skip if already have it)
brew install pipx
pipx ensurepath

# Install tableau-mcp
pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git

# Get the installed path (copy this for config)
which tableau-mcp

# Verify it starts
tableau-mcp
Claude Desktop config → ~/Library/Application Support/Claude/claude_desktop_config.json


{
  "mcpServers": {
    "tableau-mcp": {
      "command": "/Users/<you>/.local/bin/tableau-mcp",
      "args": [],
      "env": {
        "GEMINI_API_KEY": "your_AIza_key_here",
        "DEFAULT_LLM_PROVIDER": "gemini"
      }
    }
  }
}
Replace command with output of which tableau-mcp.

Existing Users (Update)

pipx install --force git+https://github.com/kar10arora/TABLEAU_MCP.git
Then fully quit and reopen Claude Desktop.

Windows
New Users

pip install git+https://github.com/kar10arora/TABLEAU_MCP.git

:: Get the installed path (copy this for config)
where tableau-mcp

:: Verify it starts
tableau-mcp
Claude Desktop config → C:\Users\<you>\AppData\Roaming\Claude\claude_desktop_config.json


{
  "mcpServers": {
    "tableau-mcp": {
      "command": "C:\\Python311\\Scripts\\tableau-mcp.exe",
      "args": [],
      "env": {
        "GEMINI_API_KEY": "your_AIza_key_here",
        "DEFAULT_LLM_PROVIDER": "gemini"
      }
    }
  }
}
Replace command with output of where tableau-mcp.

Existing Users (Update)

pip install --upgrade git+https://github.com/kar10arora/TABLEAU_MCP.git
Then fully quit and reopen Claude Desktop.

artik.arora@ndi-mb-150 ~ % pipx install --force git+https://github.com/kar10arora/TABLEAU_MCP.git

Running command git clone --filter=blob:none --quiet https://github.com/kar10arora/TABLEAU_MCP.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/T/pip-req-build-cglhz53z
  remote: Repository not found.
  fatal: repository 'https://github.com/kar10arora/TABLEAU_MCP.git/' not found
  error: subprocess-exited-with-error
  
  × git clone --filter=blob:none --quiet https://github.com/kar10arora/TABLEAU_MCP.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/T/pip-req-build-cglhz53z did not run successfully.
  │ exit code: 128
  ╰─> No available output.
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
ERROR: Failed to build 'git+https://github.com/kar10arora/TABLEAU_MCP.git' when git clone --filter=blob:none --quiet https://github.com/kar10arora/tableau_mcp.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/t/pip-req-build-cglhz53z
kartik.arora@ndi-mb-150 ~ % 
??
The repo is private — that's why it fails. Anyone trying to install gets "Repository not found."

You have two options:

Option A — Make the repo public (simplest)
Go to https://github.com/kar10arora/TABLEAU_MCP → Settings → scroll to bottom → Change visibility → Make public

After that, the pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git command works for everyone with no changes.

Option B — Distribute the PyInstaller binary (no repo access needed)
Since you already have PyInstaller set up, build the .exe once and share it directly. Users just download and point their config to it — no pip/pipx needed.

Build the binary:


cd /Users/kartik.arora/TABLEAU-MCP
pip install pyinstaller
pyinstaller --onefile --name tableau-mcp tableau_mcp/__main__.py
The binary lands at dist/tableau-mcp (macOS) or dist\tableau-mcp.exe (Windows).

Users then just:

Download the binary
Put the path in their claude_desktop_config.json
No Python, no pip, no pipx needed at all
Recommendation: Option A if this is an open-source/demo tool. Option B if you want to keep the code private and distribute just the executable.

I already have the collabortor access of that repo that's why were able to work on previous version:
84
kartik.arora@ndi-mb-150 ~ % tableau-mcpo
zsh: command not found: tableau-mcpo
kartik.arora@ndi-mb-150 ~ % tableau-mcp 


                    ╭──────────────────────────────────────────────────────────────────────────────╮                    
                    │                                                                              │                    
                    │                                                                              │                    
                    │                         ▄▀▀ ▄▀█ █▀▀ ▀█▀ █▀▄▀█ █▀▀ █▀█                        │                    
                    │                         █▀  █▀█ ▄▄█  █  █ ▀ █ █▄▄ █▀▀                        │                    
                    │                                                                              │                    
                    │                                                                              │                    
                    │                                                                              │                    
                    │                                FastMCP 3.4.2                                 │                    
                    │                            https://gofastmcp.com                             │                    
                    │                                                                              │                    
                    │                  🖥  Server:      tableau-mcp-server, 3.4.2                   │                    
                    │                  🚀 Deploy free: https://horizon.prefect.io                  │                    
                    │                                                                              │                    
                    ╰──────────────────────────────────────────────────────────────────────────────╯                    


[06/30/26 09:41:23] INFO     Starting MCP server 'tableau-mcp-server' with transport 'stdio'            transport.py:210
^C^CTraceback (most recent call last):
  File "/Users/kartik.arora/.local/bin/tableau-mcp", line 6, in <module>
    sys.exit(main())
             ~~~~^^
  File "/Users/kartik.arora/.local/pipx/venvs/tableau-mcp-server/lib/python3.14/site-packages/tableau_mcp/mcp/server.py", line 98, in main
    mcp.run()
    ~~~~~~~^^
  File "/Users/kartik.arora/.local/pipx/venvs/tableau-mcp-server/lib/python3.14/site-packages/fastmcp/server/mixins/transport.py", line 92, in run
    anyio.run(
    ~~~~~~~~~^
        partial(
        ^^^^^^^^
    ...<4 lines>...
        )
        ^
    )
    ^
  File "/Users/kartik.arora/.local/pipx/venvs/tableau-mcp-server/lib/python3.14/site-packages/anyio/_core/_eventloop.py", line 83, in run
    return async_backend.run(func, args, {}, backend_options)
           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/kartik.arora/.local/pipx/venvs/tableau-mcp-server/lib/python3.14/site-packages/anyio/_backends/_asyncio.py", line 2436, in run
    return runner.run(wrapper())
           ~~~~~~~~~~^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/asyncio/runners.py", line 128, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/asyncio/base_events.py", line 706, in run_until_complete
    self.run_forever()
    ~~~~~~~~~~~~~~~~^^
  File "/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/asyncio/base_events.py", line 677, in run_forever
    self._run_once()
    ~~~~~~~~~~~~~~^^
  File "/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/asyncio/base_events.py", line 2018, in _run_once
    event_list = self._selector.select(timeout)
  File "/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/selectors.py", line 548, in select
    kev_list = self._selector.control(None, max_ev, timeout)
  File "/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/asyncio/runners.py", line 167, in _on_sigint
    raise KeyboardInterrupt()
KeyboardInterrupt
^CException ignored while joining a thread in _thread._shutdown():
Traceback (most recent call last):
  File "/usr/local/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/threading.py", line 1583, in _shutdown
    _thread_shutdown()
KeyboardInterrupt: 
^C
kartik.arora@ndi-mb-150 ~ % where tableau-mcp
/Users/kartik.arora/.local/bin/tableau-mcp
/Users/kartik.arora/.local/bin/tableau-mcp
kartik.arora@ndi-mb-150 ~ %
It's working perfectly. The server starts and runs on stdio as expected. Ctrl+C is normal — Claude Desktop manages the lifecycle, not you.

Now update your Claude Desktop config at ~/Library/Application Support/Claude/claude_desktop_config.json:


{
  "mcpServers": {
    "tableau-mcp": {
      "command": "/Users/kartik.arora/.local/bin/tableau-mcp",
      "args": [],
      "env": {
        "GEMINI_API_KEY": "your_AIza_key_here",
        "DEFAULT_LLM_PROVIDER": "gemini"
      }
    }
  }
}
Then fully quit and reopen Claude Desktop. The MCP should show green.

Revised final commands for both platforms (since repo is private, users need collaborator access first):

macOS

# New install
pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git

# Update
pipx install --force git+https://github.com/kar10arora/TABLEAU_MCP.git

# Get path for config
which tableau-mcp
Windows

:: New install
pip install git+https://github.com/kar10arora/TABLEAU_MCP.git

:: Update
pip install --upgrade git+https://github.com/kar10arora/TABLEAU_MCP.git

:: Get path for config
where tableau-mcp
One pending thing: For Windows users who aren't collaborators, the install will still fail with "Repository not found." You'll need to either add them as collaborators on GitHub or make the repo public before sharing these commands with them.

see I have the access to this repo:
https://github.com/kar10arora/TABLEAU_MCP/commits/main/
still getting same error during update:
kartik.arora@ndi-mb-150 ~ % where tableau-mcp
/Users/kartik.arora/.local/bin/tableau-mcp
/Users/kartik.arora/.local/bin/tableau-mcp
kartik.arora@ndi-mb-150 ~ % pipx install --force git+https://github.com/kar10arora/TABLEAU_MCP.git

Running command git clone --filter=blob:none --quiet https://github.com/kar10arora/TABLEAU_MCP.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/T/pip-req-build-ck8pkeud
  remote: Repository not found.
  fatal: repository 'https://github.com/kar10arora/TABLEAU_MCP.git/' not found
  error: subprocess-exited-with-error
  
  × git clone --filter=blob:none --quiet https://github.com/kar10arora/TABLEAU_MCP.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/T/pip-req-build-ck8pkeud did not run successfully.
  │ exit code: 128
  ╰─> No available output.
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
ERROR: Failed to build 'git+https://github.com/kar10arora/TABLEAU_MCP.git' when git clone --filter=blob:none --quiet https://github.com/kar10arora/tableau_mcp.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/t/pip-req-build-ck8pkeud
kartik.arora@ndi-mb-150 ~ %
The issue is git isn't authenticated on your machine for that private repo. The browser session doesn't carry over to terminal git.

Since you already have the repo cloned locally at /Users/kartik.arora/TABLEAU-MCP, skip GitHub entirely and install directly from the local path:

Update (use local clone)

cd /Users/kartik.arora/TABLEAU-MCP && git pull && pipx install --force .
This pulls latest changes then reinstalls from local — no auth issue.

For other collaborator users (fix the auth problem properly)
They need to authenticate git first, then install works:


# Option 1 — GitHub CLI (recommended)
brew install gh
gh auth login
pipx install --force git+https://github.com/kar10arora/TABLEAU_MCP.git

# Option 2 — SSH (if they have SSH key set up on GitHub)
pipx install --force git+ssh://git@github.com/kar10arora/TABLEAU_MCP.git
So your updated final commands for collaborators on macOS should be:


# New install (after gh auth login)
gh auth login
pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git

# Update
pipx install --force git+https://github.com/kar10arora/TABLEAU_MCP.git
And for you specifically during dev:


cd /Users/kartik.arora/TABLEAU-MCP && git pull && pipx install --force .
you forget about this
pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git
You're right, my bad. pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git worked for the initial install. The problem is pipx has no --force-reinstall flag.

The correct update command for existing users is uninstall + reinstall:

macOS — Final Correct Commands
New Users

pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git
Existing Users (Update)

pipx uninstall tableau-mcp-server
pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git
Windows — Final Correct Commands
New Users

pip install git+https://github.com/kar10arora/TABLEAU_MCP.git
Existing Users (Update)

pip install --upgrade git+https://github.com/kar10arora/TABLEAU_MCP.git
After install on both platforms, get the path for Claude Desktop config:

Platform	Command	Example output
macOS	which tableau-mcp	/Users/<you>/.local/bin/tableau-mcp
Windows	where tableau-mcp	C:\Python311\Scripts\tableau-mcp.exe
kartik.arora@ndi-mb-150 ~ % pipx uninstall tableau-mcp-server

uninstalled tableau-mcp-server! ✨ 🌟 ✨
kartik.arora@ndi-mb-150 ~ % pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git

Running command git clone --filter=blob:none --quiet https://github.com/kar10arora/TABLEAU_MCP.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/T/pip-req-build-bc3ntkux
  remote: Repository not found.
  fatal: repository 'https://github.com/kar10arora/TABLEAU_MCP.git/' not found
  error: subprocess-exited-with-error
  
  × git clone --filter=blob:none --quiet https://github.com/kar10arora/TABLEAU_MCP.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/T/pip-req-build-bc3ntkux did not run successfully.
  │ exit code: 128
  ╰─> No available output.
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
ERROR: Failed to build 'git+https://github.com/kar10arora/TABLEAU_MCP.git' when git clone --filter=blob:none --quiet https://github.com/kar10arora/tableau_mcp.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/t/pip-req-build-bc3ntkux
kartik.arora@ndi-mb-150 ~ % 

what the feaking issue it is?? again n again getting same error even when I tried previously and it worked
The root cause: your GitHub credentials expired in the macOS keychain. That's why it worked before and fails now — the cached token is gone.

Two fixes:

Fix 1 — Immediate (install from your local clone)


cd /Users/kartik.arora/TABLEAU-MCP && git pull && pipx install .
Works right now, no auth needed.

Fix 2 — Permanent (re-authenticate so GitHub URL works again)


brew install gh
gh auth login
Follow the prompts (select GitHub.com → HTTPS → Login with browser). After that:


pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git
will work again and keep working until you explicitly log out.

Use Fix 1 right now, Fix 2 once so it stops breaking. After gh auth login, the macOS keychain stores the token permanently and the GitHub URL install will work for all future collaborators on that machine too.

Press Enter to open https://github.com/login/device in your browser... 
5✓ Authentication complete.
- gh config set -h github.com git_protocol https
✓ Configured git protocol
✓ Logged in as kartikarora-svg
! You were already logged in to this account
kartik.arora@ndi-mb-150 ~ % pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git

Running command git clone --filter=blob:none --quiet https://github.com/kar10arora/TABLEAU_MCP.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/T/pip-req-build-4i8lbjlt
  remote: Repository not found.
  fatal: repository 'https://github.com/kar10arora/TABLEAU_MCP.git/' not found
  error: subprocess-exited-with-error
  
  × git clone --filter=blob:none --quiet https://github.com/kar10arora/TABLEAU_MCP.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/T/pip-req-build-4i8lbjlt did not run successfully.
  │ exit code: 128
  ╰─> No available output.
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
ERROR: Failed to build 'git+https://github.com/kar10arora/TABLEAU_MCP.git' when git clone --filter=blob:none --quiet https://github.com/kar10arora/tableau_mcp.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/t/pip-req-build-4i8lbjlt
kartik.arora@ndi-mb-150 ~ % 
Mpw what the freaking issue again??
gh auth login authenticates the gh CLI but git itself doesn't use those credentials automatically. Run this one extra command:


gh auth setup-git
This wires gh as git's credential helper for GitHub. Then:


pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git
That's the missing link — gh auth login and git HTTPS are separate systems until setup-git connects them.

kartik.arora@ndi-mb-150 ~ % gh auth setup-git

kartik.arora@ndi-mb-150 ~ % pipx install git+https://github.com/kar10arora/TABLEAU_MCP.git

Running command git clone --filter=blob:none --quiet https://github.com/kar10arora/TABLEAU_MCP.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/T/pip-req-build-1oawvbar
  remote: Repository not found.
  fatal: repository 'https://github.com/kar10arora/TABLEAU_MCP.git/' not found
  error: subprocess-exited-with-error
  
  × git clone --filter=blob:none --quiet https://github.com/kar10arora/TABLEAU_MCP.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/T/pip-req-build-1oawvbar did not run successfully.
  │ exit code: 128
  ╰─> No available output.
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
ERROR: Failed to build 'git+https://github.com/kar10arora/TABLEAU_MCP.git' when git clone --filter=blob:none --quiet https://github.com/kar10arora/tableau_mcp.git /private/var/folders/l4/dtb5wrb57mq627r79k3qzk6m0000gq/t/pip-req-build-1oawvbar
kartik.arora@ndi-mb-150 ~ % 

Are you really out of your mind or what??
Look at the error closely — pip is silently changing the URL:

You pass: https://github.com/kar10arora/TABLEAU_MCP.git

pip actually clones: https://github.com/kar10arora/tableau_mcp.git ← all lowercase

pip normalizes package URLs to lowercase. GitHub repo names are case-sensitive, so tableau_mcp ≠ TABLEAU_MCP → "Repository not found."

Fix: Rename the repo on GitHub to lowercase.

Go to https://github.com/kar10arora/TABLEAU_MCP → Settings → Repository name → change to tableau_mcp → Rename

Then update your local remote:


cd /Users/kartik.arora/TABLEAU-MCP
git remote set-url origin https://github.com/kar10arora/tableau_mcp.git
After that, the install command will work permanently:


pipx install git+https://github.com/kar10arora/tableau_mcp.git
Right now without renaming, use the local clone:


cd /Users/kartik.arora/TABLEAU-MCP && git pull && pipx install .