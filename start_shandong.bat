@echo off
setlocal

cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Starting shandong dashboard...
"%PYTHON_EXE%" scripts\start_dashboard.py

if errorlevel 1 (
    echo.
    echo Dashboard startup failed. Please check the error message above.
    pause
    exit /b 1
)

endlocal

