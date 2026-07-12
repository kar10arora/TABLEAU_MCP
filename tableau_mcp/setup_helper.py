"""
tableau-mcp-setup command.
Prints the exact claude_desktop_config.json snippet the user needs to paste.
"""

import sys
import os
import json
import platform


def _find_tableau_mcp_exe() -> str:
    """Find the tableau-mcp executable path."""
    scripts_dir = os.path.dirname(sys.executable)

    if platform.system() == "Windows":
        candidates = [
            os.path.join(scripts_dir, "tableau-mcp.exe"),
            os.path.join(scripts_dir, "Scripts", "tableau-mcp.exe"),
        ]
    else:
        candidates = [
            os.path.join(scripts_dir, "tableau-mcp"),
            os.path.join(os.path.dirname(scripts_dir), "bin", "tableau-mcp"),
        ]

    for path in candidates:
        if os.path.exists(path):
            return path

    # Fallback: use python -m tableau_mcp
    return None


def _config_snippet(exe_path: str) -> dict:
    if exe_path:
        entry = {
            "command": exe_path,
            "args": [],
            "env": {
                "GEMINI_API_KEY": "YOUR_GEMINI_API_KEY_HERE",
                "DEFAULT_LLM_PROVIDER": "gemini"
            }
        }
    else:
        entry = {
            "command": sys.executable,
            "args": ["-m", "tableau_mcp"],
            "env": {
                "GEMINI_API_KEY": "YOUR_GEMINI_API_KEY_HERE",
                "DEFAULT_LLM_PROVIDER": "gemini"
            }
        }
    return entry


def print_config():
    """Entry point for tableau-mcp-setup command."""
    exe = _find_tableau_mcp_exe()

    print("\n" + "="*60)
    print("  Tableau MCP Server — Setup Complete")
    print("="*60)
    print("\nStep 1: Get your free Gemini API key at:")
    print("        https://aistudio.google.com/apikey\n")
    print("Step 2: Open your Claude Desktop config file:")

    if platform.system() == "Windows":
        appdata = os.environ.get("APPDATA", r"C:\Users\<you>\AppData\Roaming")
        print(f"        {appdata}\\Claude\\claude_desktop_config.json")
    elif platform.system() == "Darwin":
        print("        ~/Library/Application Support/Claude/claude_desktop_config.json")
    else:
        print("        ~/.config/Claude/claude_desktop_config.json")

    print('\nStep 3: Add this inside "mcpServers": { ... }\n')

    snippet = {"tableau-mcp": _config_snippet(exe)}
    print(json.dumps(snippet, indent=2))

    print("\nStep 4: Replace YOUR_GEMINI_API_KEY_HERE with your actual key")
    print("\nStep 5: Fully quit and reopen Claude Desktop\n")
    print("="*60)
    print("  Done! You should see tableau-mcp tools in Claude Desktop.")
    print("="*60 + "\n")

    if not exe:
        print("NOTE: Could not find tableau-mcp executable.")
        print(f"      Using Python fallback: {sys.executable} -m tableau_mcp")
        print("      This works the same way.\n")


if __name__ == "__main__":
    print_config()
