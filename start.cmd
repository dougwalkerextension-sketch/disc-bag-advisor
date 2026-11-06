@echo off
setlocal
set "APP_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%APP_PYTHON%" set "APP_PYTHON=%~dp0.runtime\python.exe"
if not exist "%APP_PYTHON%" (
  echo No local Python environment found. Create .venv and install requirements.txt. See README.md.
  exit /b 1
)
"%APP_PYTHON%" "%~dp0app.py"
exit /b %ERRORLEVEL%
