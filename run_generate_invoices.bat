@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Virtual environment not found: .venv
  echo Create it first with: python -m venv .venv
  pause
  exit /b 1
)

if not exist "output\invoices" (
  mkdir "output\invoices"
)

".venv\Scripts\python.exe" generate_invoices.py

echo.
echo Done. Check output\invoices
explorer "output\invoices"
pause