@echo off
echo ============================================
echo  Tableau MCP Server - Installation
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

echo [1/3] Python found:
python --version

REM Create venv in user's AppData so it's isolated
set INSTALL_DIR=%APPDATA%\tableau-mcp
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo.
echo [2/3] Installing tableau-mcp (this takes 2-3 minutes)...
python -m venv "%INSTALL_DIR%\venv" >nul 2>&1
"%INSTALL_DIR%\venv\Scripts\pip.exe" install --quiet --upgrade pip
"%INSTALL_DIR%\venv\Scripts\pip.exe" install --quiet tableau-mcp-kartik

if errorlevel 1 (
    echo [ERROR] Installation failed.
    pause
    exit /b 1
)

REM Copy the launcher bat to INSTALL_DIR
copy /y "%~dp0tableau-mcp.bat" "%INSTALL_DIR%\tableau-mcp.bat" >nul

echo.
echo [3/3] Done!
echo.
echo ============================================
echo  Setup complete! Now configure Claude Desktop
echo ============================================
echo.
echo Add this to your claude_desktop_config.json:
echo.
echo   "tableau-mcp": {
echo     "command": "%INSTALL_DIR%\tableau-mcp.bat",
echo     "env": {
echo       "GEMINI_API_KEY": "YOUR_KEY_HERE",
echo       "DEFAULT_LLM_PROVIDER": "gemini"
echo     }
echo   }
echo.
echo Get your free Gemini key at: https://aistudio.google.com/apikey
echo.
pause
