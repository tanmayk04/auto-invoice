@echo off
setlocal

cd /d "%~dp0"

echo [1/3] Creating virtual environment...
python --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python is not installed or not in PATH.
  echo Install Python 3.11+ and check "Add Python to PATH".
  pause
  exit /b 1
)

if not exist ".venv" (
  python -m venv .venv
)

echo [2/3] Installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install pandas openpyxl reportlab

echo [3/3] Setup complete!
echo Next time, run: run_generate_invoices.bat
pause