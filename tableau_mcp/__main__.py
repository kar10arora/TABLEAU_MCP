"""
Entry point for running tableau_mcp as a module or compiled binary.
This file allows:
  - python -m tableau_mcp
  - PyInstaller to compile into standalone executable
"""

from tableau_mcp.mcp.server import main

if __name__ == "__main__":
    main()
